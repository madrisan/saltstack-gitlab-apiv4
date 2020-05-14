# A SaltStack module for interacting with GitLab API v4

[![License](https://img.shields.io/badge/License-Apache--2.0-blue.svg)](https://spdx.org/licenses/Apache-2.0.html)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/1e5033bc92474eea86dd5a8889f2af8d)](https://www.codacy.com/manual/madrisan/saltstack-gitlab-apiv4?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=madrisan/saltstack-gitlab-apiv4&amp;utm_campaign=Badge_Grade)
[![Maintainability](https://api.codeclimate.com/v1/badges/55c3b99a3c91820304be/maintainability)](https://codeclimate.com/github/madrisan/saltstack-gitlab-apiv4/maintainability)

A SaltStack extension module for interacting with GitLab API v4.

GitLab API documentation: https://docs.gitlab.com/ee/api

This module requires a configuration profile to be configured in either the minion or, as in our implementation, in the master configuration file (`/etc/salt/master.d/gitlab.conf`).

    gitlab:
      api_url: https://gitlab.example.com
      token: peWcBiMOS9HrZG15peWc

This Python module should be saved as `salt/_modules/gitlab.py`.

### Implemented Methods

    def http_delete(path, **kwargs)
    def http_get(path, **kwargs)
    def http_post(path, data=None, json=None, **kwargs)
    def http_put(path, data=None, json=None, **kwargs)

### Usage example from another execution module

Here's an example of the usage of this module from another salt execution module:
```
import logging

log = logging.getLogger(__name__)

def get_user_id(username):
    """
    Return the GitLab informations for a given user.
    """
    resource = '/users?username={0}'.format(username)
    try:
        response = __salt__['gitlab.http_get'](resource)
        user_id = response[0].get('id', None)
    except:
        log.warning(('Cannot find in GitLab the user id of {0}'
                     .format(username)))
        user_id = None

    return user_id
```
