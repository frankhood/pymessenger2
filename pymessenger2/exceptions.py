# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

#===============================================================================
# Taken from https://github.com/jgorset/facepy/blob/master/facepy/exceptions.py
#===============================================================================
class FacebookError(Exception):
    def __init__(self, message=None, code=None, error_data=None, error_subcode=None,
                 is_transient=None, error_user_title=None, error_user_msg=None,
                 fbtrace_id=None):
        self.message = message
        self.code = code
        self.error_data = error_data
        self.error_subcode = error_subcode
        self.is_transient = is_transient
        self.error_user_title = error_user_title
        self.error_user_msg = error_user_msg
        self.fbtrace_id = fbtrace_id

        if self.code:
            message = '[%s] %s' % (self.code, self.message)

        super(FacebookError, self).__init__(message)
        
class OAuthError(FacebookError):
    pass