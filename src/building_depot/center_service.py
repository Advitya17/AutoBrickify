'''
bd_service.py
~~~~~~


@copyright: (c) 2013 SynergyLabs
@license:   UCSD License. See License file for details.
'''
from .bd_service import BuildingDepotService


class CenterService(BuildingDepotService):

    '''It is the API for CenterService.'''

    def __init__(self, base_url, api_key, username=None,
                 auth_token=None, expiration=None, verify=False):
        super(CenterService, self).__init__('%s' % base_url,
                                            username=username,
                                            api_key=api_key,
                                            auth_token=auth_token,
                                            expiration=expiration,
                                            verify=verify)

    @property
    def api_url(self):
        return '%s/api' % self.base_url

    def create_session(self, username, password):
        ''' create a session on Building Depot Server (login)

        using api : POST /sessions

        return `api_key`, `auth_token`, `expiration`
        '''
        auth = (username, password)
        url = '%s/sessions' % self.api_url
        r = self.post(url, headers=self._init_headers, auth=auth)
        response = r.json()
        self.api_key = response['api_key']
        self.auth_token = response['auth_token']
        self.expiration = response['expiration']
        return self.api_key, self.auth_token, self.expiration

    def view_session(self):
        ''' view the information of a session after login

        using api : GET /sessions/<auth_token>

        return the orignal response (dict)
        {
            'auth_token': Authentication Token,
            'user': {
                'api_key': Users API key,
                'uuid': Users Unique Identifier,
                'email': Users email address,
            },
            'expiration': Expiration time for auth_token,
            'uri': Resource Uri,
        }
        '''
        url = '%s/sessions/%s' % (self.api_url, self.auth_token)
        r = self.get(url, headers=self._init_headers)
        response = r.json()
        return response

    def update_session(self):
        '''
        renew a session before expiration
        using api : POST /sessions/<auth_token>
        '''
        url = '%s/sessions/%s' % (self.api_url, self.auth_token)
        self.post(url, headers=self._init_headers)

    def delete_session(self, auth_token):
        '''
        delete a session (log out)
        using api : DELETE /sessions/<auth_token>
        '''
        url = '%s/sessions/%s' % (self.api_url, auth_token)
        self.delete(url, headers=self._init_headers)

    def create_user(self, email, password, name,
                    access_level=1, enabled=False):
        '''
        create a user account
        using api: POST /user
        return uri (string) - Uri of newly created User resource item
        '''
        url = '%s/users' % self.api_url
        data = {
            'email': email,
            'password': password,
            'name': name,
            'access_level': access_level,
            'enabled': enabled
        }
        r = self.post(url, json_data=data, headers=self._init_headers)
        response = r.json()
        return response['uri']

    def view_user(self, email):
        '''
        view the information of a user
        using api: GET /users/<email>
        return the orignal result
        {
            'email': (string) - User email address
            'name': (string) - User Full Name
            'enabled': (boolean) - User account enabled status
            'activated': (boolean) - User account activation status
            'access_level': (int) - User Access (Authorization) Level
            'api_key': (int) - User API Key
            'auth_secret': (int) - User Authentication Secret
                                   (Not yet implemented)
            'created_time': (string) - ISO Formatted Admin creation time
            'uri': (string) - Resource Uri
        }
        '''
        url = '%s/users/%s' % (self.api_url, email)
        r = self.get(url, headers=self._init_headers)
        response = r.json()
        return response

    def register_user(self, email, password, name):
        '''
        register a new user account
        using api: POST /registration
        return the orignal result
        '''
        url = '%s/registration' % self.api_url
        data = {
            'email': email,
            'password': password,
            'name': name,
        }
        r = self.post(url, json_data=data, headers=self._init_headers)
        return r.json()

    def activate_user(self, activation_key):
        '''
        active the user account associate to activation key
        using api: GET /registration/<activation_key>
        '''
        url = '%s/registration/%s' % (self.api_url, activation_key)
        r = self.get(url, headers=self._init_headers)
        return r.json()['activated']

    def update_user(self, email, **data):
        '''
        Updates a user account. Any of the specified Json Parameters can be
        passed to update the user account.
        using api: POST /users/<email>
        Json param:
            - password (string) - Users current password, if updating password
            - name (string) - Users name
            - auth_secret (string) - Users Authentication secret
                                     (Not yet implemented)
            - access_level (int) - Users Authorization level
            - enabled (boolean) - User enabled status
            - activated (boolean) - User activated status
        '''
        url = '%s/users/%s' % (self.api_url, email)
        self.post(url, json_data=data, headers=self._init_headers)

    def delete_user(self, email):
        '''
        Deletes the User account associated with email.
        using api: DELETE /users/<email>
        '''
        url = '%s/users/%s' % (self.api_url, email)
        self.delete(url, headers=self._init_headers)
