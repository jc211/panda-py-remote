"""
Introduction
------------

panda-py is a Python library for the Franka Emika Robot System
that allows you to program and control the robot in real-time.


"""

import base64
import configparser
import dataclasses
import hashlib
import json as json_module
import logging
import os
import ssl
import time
import typing
from urllib import parse
import httpx
import trio
from trio_websocket import open_websocket_url
from trio_util import trio_async_generator

__version__ = '0.8.1'

_logger = logging.getLogger('desk')
_logger.setLevel(logging.DEBUG)
_logger.addHandler(logging.StreamHandler())

TOKEN_PATH = '~/.panda_py/token.conf'

@dataclasses.dataclass
class Token:
  """
  Represents a Desk token owned by a user.
  """
  id: str = ''
  owned_by: str = ''
  token: str = ''

class Desk:
    """
    Connects to the control unit running the web-based Desk interface
    to manage the robot. Use this class to interact with the Desk
    from Python, e.g. if you use a headless setup. This interface
    supports common tasks such as unlocking the brakes, activating
    the FCI etc.

    Newer versions of the system software use role-based access
    management to allow only one user to be in control of the Desk
    at a time. The controlling user is authenticated using a token.
    The :py:class:`Desk` class saves those token in :py:obj:`TOKEN_PATH`
    and will use them when reconnecting to the Desk, retaking control.
    Without a token, control of a Desk can only be taken, if there is
    no active claim or the controlling user explicitly relinquishes control.
    If the controlling user's token is lost, a user can take control
    forcefully (cf. :py:func:`Desk.take_control`) but needs to confirm
    physical access to the robot by pressing the circle button on the
    robot's Pilot interface.
    """
    def __init__(self,
                hostname: str,
                platform: str = 'panda') -> None:
        
        self._legacy = False
        if platform.lower() in [
            'panda', 'fer', 'franka_emika_robot', 'frankaemikarobot'
        ]:
            self._platform = 'panda'
        elif platform.lower() in ['fr3', 'frankaresearch3', 'franka_research_3']:
            self._platform = 'fr3'
        else:
            raise ValueError("Unknown platform! Must be either 'panda' or 'fr3'!")
        
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        self._session = httpx.AsyncClient(verify=ctx)

        self._hostname = hostname
        self._platform = platform
        self._logged_in = False
        self._username = 'Not set'
        self._token = self._load_token()
    
    def logged_in(self) -> bool:
        """
        Returns whether the Desk is logged in.
        """
        return self._logged_in  
        
    @staticmethod
    def encode_password(username: str, password: str) -> str:
        """
        Encodes the password into the form needed to log into the Desk interface.
        """
        bytes_str = ','.join([
            str(b) for b in hashlib.sha256((
                f'{password}#{username}@franka').encode('utf-8')).digest()
        ])
        return base64.encodebytes(bytes_str.encode('utf-8')).decode('utf-8')
    
    async def login(self, username: str, password: str) -> None:
        """
        Uses the object's instance parameters to log into the Desk.
        The :py:class`Desk` class's constructor will try to connect
        and login automatically.
        """
        login = await self._request(
            'post',
            '/admin/api/login',
            json={
                'login': username,
                'password': self.encode_password(username, password)
            },
            )
        self._session.cookies.set('authorization', login.text)
        self._logged_in = True
        self._username = username
        _logger.info('Login succesful.')  
        

    async def system_status_aiter(self):
        async with self.connect(f"desk/api/system/status") as websocket:
            while True:
                msg = await websocket.recv() # type: ignore
                msg = json_module.loads(msg)
                yield msg
                
    async def check_has_control(self):
        token = await self._get_active_token()
        return self._token.id == token.id
    
    async def take_control(self, force: bool = False) -> bool:
        """
        Takes control of the Desk, generating a new control token and saving it.
        If `force` is set to True, control can be taken forcefully even if another
        user is already in control. However, the user will have to press the circle
        button on the robot's Pilot within an alotted amount of time to confirm
        physical access.

        For legacy versions of the Desk, this function does nothing.
        """
        if self._legacy:
            return True
        active = await self._get_active_token()
        if active.id != '' and self._token.id == active.id:
            _logger.info('Retaken control.')
            return True
        if active.id != '' and not force:
            _logger.warning('Cannot take control. User %s is in control.',
                        active.owned_by)
            return False
        response = await self._request(
            'post',
            f'/admin/api/control-token/request{"?force" if force else ""}',
            json={
                'requestedBy': self._username
            })
        response = response.json()
        if force:
            r = await self._request('get',
                                '/admin/api/safety')
            timeout = r.json()['tokenForceTimeout']
            _logger.warning(
                'You have %d seconds to confirm control by pressing circle button on robot.',
                timeout)
        
            with trio.move_on_after(timeout) as cancel_scope:
                await self.wait_for_press('circle')

            if cancel_scope.cancel_called:
                _logger.warning('Control not confirmed. Giving up.')
                return False
                    
        self._save_token(
            Token(str(response['id']), self._username, response['token']))
        _logger.info('Taken control.')
        return True
    
    @trio_async_generator
    async def system_status_generator(self):            
        async with self.connect('desk/api/system/status') as websocket:
            while True:
                event = await websocket.get_message()
                yield json_module.loads(event)

    @trio_async_generator
    async def events_generator(self):            
        async with self.connect('desk/api/navigation/events') as websocket:
            while True:
                event = await websocket.get_message()
                yield json_module.loads(event)
    
    async def wait_for_brakes_to_open(self):
        async with self.system_status_generator() as status_gen:
            async for status in status_gen:
                if all(status['brakesOpen']):
                    return
    
    async def wait_for_brakes_to_close(self):
        async with self.system_status_generator() as status_gen:
            async for status in status_gen:
                brakesClosed = [not b for b in status['brakesOpen']]
                if all(brakesClosed):
                    return
    
    async def wait_for_press(self, button: typing.Literal['circle', 'check', 'cross']):
        async with self.events_generator() as event_gen:
            async for e in event_gen:
                if button in e.keys() and e[button] == True:
                    return e
                
    async def wait_for_release(self, button: typing.Literal['circle', 'check', 'cross']):
        async with self.events_generator() as event_gen:
            async for e in event_gen:
                if button in e.keys() and e[button] == False:
                    return e
    
    async def lock(self, force: bool = True) -> None:
        """
        Locks the brakes. API call blocks until the brakes are locked.
        """
        if self._platform == 'panda':
            url = '/desk/api/robot/close-brakes'
        elif self._platform == 'fr3':
            url = '/desk/api/joints/lock'
        
        await self._request('post',
                url,
                files={'force': str(force).encode('utf-8')},
                timeout=50,
                headers={'X-Control-Token': self._token.token})
    
    async def unlock(self, force: bool = True) -> None:
        """
        Unlocks the brakes. API call blocks until the brakes are unlocked.
        """
        if self._platform == 'panda':
            url = '/desk/api/robot/open-brakes'
        elif self._platform == 'fr3':
            url = '/desk/api/joints/unlock'
        await self._request('post',
                url,
                files={'force': str(force).encode('utf-8')},
                timeout=50,
                headers={'X-Control-Token': self._token.token})

    async def reboot(self) -> None:
        """
        Reboots the robot hardware (this will close open connections).
        """
        await self._request('post',
                    '/admin/api/reboot',
                    headers={'X-Control-Token': self._token.token})

    async def activate_fci(self) -> None:
        """
        Activates the Franka Research Interface (FCI). Note that the
        brakes must be unlocked first. For older Desk versions, this
        function does nothing.
        """
        if not self._legacy:
            await self._request('post',
                            '/admin/api/control-token/fci',
                            json={'token': self._token.token})

    async def deactivate_fci(self) -> None:
        """
        Deactivates the Franka Research Interface (FCI). For older
        Desk versions, this function does nothing.
        """
        if not self._legacy:
            await self._request('delete',
                        '/admin/api/control-token/fci',
                        json={'token': self._token.token})
        
    async def _get_active_token(self) -> Token:
        token = Token()
        if self._legacy:
            return token
        response = await self._request("get", "/admin/api/control-token")
        response = response.json()
        if response['activeToken'] is not None:
            token.id = str(response['activeToken']['id'])
            token.owned_by = response['activeToken']['ownedBy']
        return token

    
    def _load_token(self) -> Token:
        config_path = os.path.expanduser(TOKEN_PATH)
        config = configparser.ConfigParser()
        token = Token()
        if os.path.exists(config_path):
            config.read(config_path)
            if config.has_section(self._hostname):
                token.id = config.get(self._hostname, 'id')
                token.owned_by = config.get(self._hostname, 'owned_by')
                token.token = config.get(self._hostname, 'token')
        return token

    def _save_token(self, token: Token) -> None:
        config_path = os.path.expanduser(TOKEN_PATH)
        config = configparser.ConfigParser()
        if os.path.exists(config_path):
            config.read(config_path)
        config[self._hostname] = {
            'id': token.id,
            'owned_by': token.owned_by,
            'token': token.token
        }
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, 'w') as config_file:
            config.write(config_file)
        self._token = token
    
    async def _request(self, 
                    method: typing.Literal["get", "post", "delete"], 
                    url:str, 
                    headers: typing.Optional[typing.Dict[str, str]] = None,
                    json: typing.Optional[typing.Dict[str, str]]  = None,
                    files: typing.Optional[typing.Dict[str, str]]  = None,
                    timeout: int = 5) -> httpx.Response:
  
        url = parse.urljoin(f"https://{self._hostname}", url)
        fun = getattr(self._session, method)
        kwargs = {}
        if method != 'get':
            kwargs['json'] = json
            kwargs['files'] = files
        kwargs['headers'] = headers
        
        response = await fun(
            url,
            timeout=timeout,
            **kwargs
            )
        if response.status_code != 200:
            print(f"Attemped to connect to {url} with method {method} and got response {response.text}")
            raise ConnectionError(response.text)
        return response
        
    def connect(self, address):
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        headers = [("authorization", f"{self._session.cookies.get('authorization')}")]
        return open_websocket_url(f"wss://{self._hostname}/{address}", ssl_context=ctx, extra_headers=headers)
    