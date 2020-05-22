"""
Module for interacting with the GitLab APIs v4

Copyright (C) 2020 Davide Madrisan <davide.madrisan@gmail.com>
Copyright (C) 2020 Baptiste Dauphin <baptistedauphin@protonmail.com>

:configuration: This module can be used by either passing an api_url and token
    directly or by specifying both in a configuration profile in the salt
    master/minion config. For example:

    .. code-block:: yaml

        gitlab:
          api_url: https://gitlab.example.com
          token: peWcBiMOS9HrZG15peWc
"""

# Import Python libs
from __future__ import absolute_import

# Import Salt libs
import salt.config
import salt.exceptions
import salt.utils.http
from salt.exceptions import SaltInvocationError

# Import 3rd-party libs
import salt.ext.six.moves.http_client
from salt.ext import six
from salt.ext.six.moves.urllib.parse import urljoin as _urljoin

__virtualname__ = 'gitlab'


def __virtual__():
    return __virtualname__


def _get_config():
    """
    Retrieves and return the GitLab's configuration.
    """
    try:
        master_opts = salt.config.client_config('/etc/salt/master')
    except Exception as err:
        raise SaltInvocationError(
            'No GitLab configuration found: {0}'.format(err))

    return master_opts.get('gitlab', {})


def _http_request(method,
                  path,
                  data=None,
                  formdata=False,
                  formdata_fieldname=None,
                  stream=False,
                  streaming_callback=None,
                  verify_ssl=True,
                  cert=None):
    """
    Return the result of a query to GitLab API.
    """
    gitlab_config = _get_config()

    api_url = gitlab_config.get('api_url')
    if not api_url:
        raise SaltInvocationError('No GitLab API URL found')

    token = gitlab_config.get('token')
    if not token:
        raise SaltInvocationError('No GitLab Token found')

    decode = True
    if method == 'DELETE':
        decode = False

    ca_bundle = None
    ca_certs = gitlab_config.get('ca_certs', None)
    if ca_certs and verify_ssl == True:
        ca_bundle = ca_certs

    url = _urljoin(api_url, '/api/v4' + six.text_type(path))
    log.warning(url)

    headers = {'PRIVATE-TOKEN': token}
    if method != 'POST':
        headers['Content-Type'] = 'application/json'

    response = salt.utils.http.query(url,
                                     method,
                                     ca_bundle=ca_bundle,
                                     data=data,
                                     decode=decode,
                                     decode_type='auto',
                                     formdata=formdata,
                                     formdata_fieldname=formdata_fieldname,
                                     header_dict=headers,
                                     status=True,
                                     stream=stream,
                                     streaming_callback=streaming_callback,
                                     text=True,
                                     opts=__opts__,
                                     )
    return response


def http_delete(path, **kwargs):
    """
    Make a DELETE request to the Gitlab server.
    """
    return _http_request('DELETE', path, **kwargs)


def http_get(path, **kwargs):
    """
    Send a GET request to GitLab API.
    """
    response = _http_request('GET', path, **kwargs)

    streamed = kwargs.get('stream', False)
    if streamed:
        return response

    if response.get('status', None) != salt.ext.six.moves.http_client.OK:
        raise SaltInvocationError(response.get('error'))

    return response['dict']


def http_post(path, data=None, **kwargs):
    """
    Send a POST request to GitLab API.
    """
    response = _http_request('POST',
                             path,
                             data=data,
                             **kwargs)
    if response.get('status', None) != salt.ext.six.moves.http_client.CREATED:
        raise SaltInvocationError(response.get('error'))

    return response.get('dict', {})


def http_put(path, data=None, **kwargs):
    """
    Send a PUT request to GitLab API.
    """
    return _http_request('PUT', path, data=data, **kwargs)
