# A SaltStack module for interacting with GitLab API v4

[![License](https://img.shields.io/badge/License-Apache--2.0-blue.svg)](https://spdx.org/licenses/Apache-2.0.html)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/34d9d4b1414c4d24a65bf1c4172ef636)](https://www.codacy.com/manual/madrisan/saltstack-gitlab-apiv4?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=madrisan/saltstack-gitlab-apiv4&amp;utm_campaign=Badge_Grade)
[![Maintainability](https://api.codeclimate.com/v1/badges/55c3b99a3c91820304be/maintainability)](https://codeclimate.com/github/madrisan/saltstack-gitlab-apiv4/maintainability)

A SaltStack extension module for interacting with GitLab API v4.

![](images/gitlab_logo.png?raw=true)

GitLab API documentation: <https://docs.gitlab.com/ee/api>

This module requires a configuration profile to be configured in either the minion or, as in our implementation, in the master configuration file (`/etc/salt/master.d/gitlab.conf`).

    gitlab:
      api_url: https://gitlab.example.com
      token: peWcBiMOS9HrZG15peWc

This Python module should be saved as `salt/_modules/gitlab.py`.

## Implemented Methods

| Parameter     | Description                                                             |
|:--------------|:------------------------------------------------------------------------|
| path (*str*)  | Path to query (e.g. '`/projects`'),                                     |
| data (*dict*) | Data to send as query parameters,                                       |
| json (*dict*) | Data to send in the body,                                               |
| **kwargs      | Optional arguments that `request` takes:                                |
|               | - `timeout` (*float*): Timeout to use for requests to the GitLab server,|
|               | - `stream` (*bool*): Whether the data should be streamed,               |
|               | - `verify` (*bool*\|*str*): Whether SSL certificates should be validated or the path to a CA file,|
|               | - `cert`: if string, path to ssl client cert file (`.pem`). If tuple, ('cert', 'key') pair.       |

#### `http_delete` make a DELETE request to the Gitlab server

    http_delete(path, **kwargs)
    
#### `http_get` send a GET request to the Gitlab server

    http_get(path, **kwargs)

#### `http_post` send a POST request to the Gitlab server

    http_post(path, data=None, json=None, **kwargs)

#### `http_put` send a PUT request to the Gitlab server

    http_put(path, data=None, json=None, **kwargs)

## Usage example from another execution module

1 . An example of the usage of a GET request from another salt execution module:

```python
def project_variables(project_id):
    """
    Return the GitLab variable informations for a given project.
    """
    project_variables = {}
    resource = '/projects/{0}/variables'.format(project_id)

    try:
        res = __salt__['gitlab.http_get'](resource)
        for data in res:
           key = data['key']
           data.pop('key')
           project_variables[key] = data
    except KeyError as err:
        template = "An exception of type {0} occurred. Arguments: {1!r}"
        message = template.format(type(err).__name__, err.args)
        raise salt.exceptions.CommandExecutionError(message)
```
2. An example of a POST request:

```python
def project_create_variable(project_id,
                            key,
                            value,
                            masked=False,
                            protected=False,
                            variable_type='env_var'):
    """
    Create a new GitLab project variable.
    """
    resource = '/projects/{0}/variables'.format(project_id)
    post_data = {
        'key': key,
        'value': value,
        'masked': masked,
        'protected': protected,
        'variable_type': variable_type
    }
 
    return __salt__['gitlab.http_post'](resource, json=post_data)
```

3. An example of a PUT request:

```python
def project_remove_variable(project_id, key):
    """
    Remove a GitLab project variable.
    """
    resource = ('/projects/{0}/variables/{1}'
                .format(project_id,
                        key))

    __salt__['gitlab.http_delete'](resource)
    return {}
```
