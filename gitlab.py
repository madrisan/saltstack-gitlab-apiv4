'''
Module for interacting with the GitLab APIs v4

Copyright (C) 2020 Davide Madrisan <davide.madrisan@gmail.com>

:configuration: This module can be used by either passing an api_url and token
    directly or by specifying both in a configuration profile in the salt
    master/minion config. For example:

    .. code-block:: yaml

        gitlab:
          api_url: https://gitlab.example.com
          token: peWcBiMOS9HrZG15peWc
'''

# Import Python libs
from __future__ import absolute_import
import logging
import requests

# Import Salt libs
import salt.config
import salt.exceptions
import salt.utils.url
from salt.exceptions import SaltInvocationError

# Import third party libs
HAS_LIBS = False
try:
    import requests
    HAS_LIBS = True
except Exception:
    pass

log = logging.getLogger(__name__)

__virtualname__ = 'gitlab'


def __virtual__():
    '''
    Only load this module if Python requests is installed on this minion.
    '''
    if HAS_LIBS:
        return __virtualname__
    return (False, 'The {0} execution module cannot be loaded: '
            'Python requests library is not installed.'
            .format(__virtualname__))


def _get_config():
    '''
    Retrieves and return the GitLab's configuration.

    :return:            A dictionary containing the GitLab configuration
    '''
    try:
        master_opts = salt.config.client_config('/etc/salt/master')
    except Exception as err:
        raise SaltInvocationError(
            'No GitLab configuration found: {0}'.format(err))

    return master_opts.get('gitlab', {})


def _http_request(method,
                  path,
                  data=None,
                  stream=False,
                  timeout=None,
                  verify=True,
                  cert=None,
                  json=None):
    '''
    Return the result of a query to GitLab API.
    '''
    gitlab_config = _get_config()

    api_url = gitlab_config.get('api_url')
    if not api_url:
        raise SaltInvocationError('No GitLab API URL found')

    token = gitlab_config.get('token')
    if not token:
        raise SaltInvocationError('No GitLab Token found')

    ca_certs = gitlab_config.get('ca_certs', None)
    if ca_certs and verify == True:
        verify = ca_certs

    headers = {
        'PRIVATE-TOKEN': token,
        'Content-Type': 'application/json' }

    if not path.startswith('/'):
        path = '/{}'.format(path)
    url = "{0}/api/v4{1}".format(api_url, path)

    response = requests.request(method,
                                url,
                                data=data,
                                headers=headers,
                                timeout=timeout,
                                stream=stream,
                                verify=verify,
                                cert=cert,
                                json=json)

    if response.status_code == requests.codes.not_found:
       return {}

    if response.status_code != requests.codes.ok:
        response.raise_for_status()

    return response


def http_delete(path, **kwargs):
    '''
    Make a DELETE request to the Gitlab server.
    '''
    return _http_request('delete', path, **kwargs)


def http_get(path, **kwargs):
    '''
    Send a GET request to GitLab API.
    '''
    streamed = kwargs.get('stream', False)
    response = _http_request('get', path, **kwargs)
    if (response.headers["Content-Type"] == "application/json"
        and not streamed):
        try:
            return response.json()
        except Exception as err:
            raise SaltInvocationError(
                      'Failed to parse the GET server message: {}'.format(err)
            )
    else:
        return response


def http_post(path, data=None, json=None, **kwargs):
    '''
    Send a POST request to GitLab API.
    '''
    response = _http_request('post', path, data=data, json=json, **kwargs)
    try:
        if response.headers.get("Content-Type") == "application/json":
            return response.json()
    except Exception as err:
        raise SaltInvocationError(
                  'Failed to parse the POST server message: {}'.format(err))

    return response


def http_put(path, data=None, json=None, **kwargs):
    '''
    Send a PUT request to GitLab API.
    '''
    response = _http_request('put', path, data=data, json=json, **kwargs)
    try:
        return response.json()
    except Exception as err:
        raise SaltInvocationError(
                  'Failed to parse the PUT server message: {}'.format(err))
