# A SaltStack module for interacting with GitLab API v4

[![License](https://img.shields.io/badge/License-Apache--2.0-blue.svg)](https://spdx.org/licenses/Apache-2.0.html)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/34d9d4b1414c4d24a65bf1c4172ef636)](https://www.codacy.com/manual/madrisan/saltstack-gitlab-apiv4?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=madrisan/saltstack-gitlab-apiv4&amp;utm_campaign=Badge_Grade)

A SaltStack extension module for interacting with GitLab API v4.

![](images/gitlab_logo.png?raw=true)

GitLab API documentation: <https://docs.gitlab.com/ee/api>

This module requires a configuration profile to be configured in either the minion or, as in our implementation, in the master configuration file (`/etc/salt/master.d/gitlab.conf`).

    gitlab:
      api_url: https://gitlab.example.com
      token: peWcBiMOS9HrZG15peWc

This Python module should be saved as `salt/_modules/gitlab.py`.

## Implemented Methods

| Parameter     | Description                                                                  |
|:--------------|:-----------------------------------------------------------------------------|
| path (*str*)  | Path to query (e.g. '`/projects`'),                                          |
| data (*dict*) | Data to send in the body,                                                    |
| **kwargs      | Optional arguments that `_http_request` takes:                               |
|               | - `formdata` (*bool*): The data is part of a form,                           |
|               | - `formdata_fieldname` (*string*): The field name of the form,               |
|               | - `stream` (*bool*): Whether the data should be streamed,                    |
|               | - `streaming_callback` (*function*): Callback function for stream processing,|
|               | - `verify_ssl` (*bool*\|*str*): Whether SSL certificates should be validated or the path to a CA file,|
|               | - `cert` (*string*): Path to ssl client cert file (`.pem`).                  |

#### `http_delete` make a DELETE request to the Gitlab server

    http_delete(path, **kwargs)
    
#### `http_get` send a GET request to the Gitlab server

    http_get(path, **kwargs)

#### `http_post` send a POST request to the Gitlab server

    http_post(path, data=None, **kwargs)

#### `http_put` send a PUT request to the Gitlab server

    http_put(path, data=None, **kwargs)

## Usage example from another execution module

1 . An example of the usage of a GET request from another salt execution module:

```python
from salt.exceptions import SaltInvocationError

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
        raise SaltInvocationError(message)

    return project_variables
```
2. An example of a POST request:

```python
def project_create_variable(project_id,
                            key,
                            value,
                            formdata=False,
                            formdata_fieldname=None,
                            masked=False,
                            protected=False,
                            variable_type='env_var',
                            **kwargs):
    """
    Create a new GitLab project variable.
    """
    resource = '/projects/{0}/variables'.format(project_id)
    post_data = {
        'key': key,
        'masked': masked,
        'protected': protected,
        'value': value,
        'variable_type': variable_type
    }
    if formdata and formdata_fieldname:
        post_data['formdata'] = True
        post_data['formdata_fieldname'] = formdata_fieldname
    elif formdata and not formdata_fieldname:
        raise SaltInvocationError(
                  'formdata_fieldname must be set if formdata=True')

    return __salt__['gitlab.http_post'](resource, data=post_data)
```

3. An example of a PUT request:

```python
def project_update_variable(project_id, key, **kwargs):
    """
    Update an existing GitLab project variable.
    """
    resource = '/projects/{0}/variables/{1}'.format(project_id, key)

    params = [
        'environment_scope',
        'masked',
        'protected',
        'value',
        'variable_type'
    ]
    post_data = {}
    for param in params:
        try:
            value = kwargs.pop(param)
            post_data[param] = value
        except:
            pass

    # add the all the kwargs but the ones automatically set by salt
    extra_args = dict(
        [(x, y) for x, y in kwargs.items() if not x.startswith('__')])

    return __salt__['http_put'](resource, data=post_data, **extra_args)
```

4. An example of a DELETE request:

```python
def project_remove_variable(project_id, key):
    """
    Delete a GitLab project variable.
    """
    resource = ('/projects/{0}/variables/{1}'
                .format(project_id,
                        key))

    __salt__['gitlab.http_delete'](resource)

    return {}
```

4. An example of a GET request with streamed data:

```python
# Import Python libs
import os
import zipfile

# Import Salt libs
import salt.utils.files
from salt.exceptions import SaltInvocationError

def get_artifact(project, job, destfile):
    """
    Download a GitLab artifact and save it as 'destfile'.

    Example:
        get_artifact(1234, 567890, "/data/artifact.zip")
    """
    def _file_unlink(filename):
        """
        Remove the local file 'filename'.
        """
        try:
            os.unlink(filename)
        except:
            pass

    resource = ('/projects/{0}/jobs/{1}/artifacts/'
                .format(project, job))

    _file_unlink(destfile)
    try:
        # we set stream=True so that requests doesn't download
        # the whole image into memory first.
        destfp = salt.utils.files.fopen(destfile, 'wb')
        def on_chunk(chunk):
            destfp.write(chunk)

        response = __salt__['gitlab.http_get'](resource,
                                               stream=True,
                                               streaming_callback=on_chunk)
        destfp.close()
    except Exception as err:
        raise SaltInvocationError((
            'Cannot download the artifact from GitLab (job: {0}): {1}'
            .format(job, err)))

    try:
        archive = zipfile.ZipFile(destfile)
    except Exception as err:
        raise SaltInvocationError((
            'Error opening the download artifact: {0}'
            .format(err)))

    if archive.testzip() is not None:
        _file_unlink(destfile)
        raise SaltInvocationError(
            'The zip archive is corrupted. Removing it.')

    return {
        "artifact": destfile
    }
```
