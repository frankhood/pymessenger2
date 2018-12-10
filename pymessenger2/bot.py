import os
from enum import Enum
import logging

import six
import json
import requests
from requests_toolbelt import MultipartEncoder

from pymessenger2 import utils
from pymessenger2.exceptions import OAuthError, FacebookError 
from pymessenger2.utils import AttrsEncoder

logger = logging.getLogger("pymessenger")

DEFAULT_API_VERSION = 2.6


class NotificationType(Enum):
    regular = "REGULAR"
    silent_push = "SILENT_PUSH"
    no_push = "NO_PUSH"


class Bot(object):
    def __init__(self,
                 access_token,
                 api_version=DEFAULT_API_VERSION,
                 app_secret=None,
                 verification_token=None,
                 raise_exception=False,
                 log_request=False,
                 log_response=False):
        """
            @required:
                access_token
            @optional:
                api_version
                app_secret
        """
        self.api_version = api_version
        self.app_secret = app_secret
        self.graph_url = 'https://graph.facebook.com/v{0}'.format(
            self.api_version)
        self.access_token = access_token
        self.verification_token = verification_token
        self.raise_exception = raise_exception
        self.log_request = log_request
        self.log_response = log_response

    @property
    def auth_args(self):
        if not hasattr(self, '_auth_args'):
            auth = {'access_token': self.access_token}
            if self.app_secret is not None:
                appsecret_proof = utils.generate_appsecret_proof(
                    self.access_token, self.app_secret)
                auth['appsecret_proof'] = appsecret_proof
            self._auth_args = auth
        return self._auth_args
    
    #===========================================================================
    # Section - CONFIGURATIONS -
    # https://developers.facebook.com/docs/messenger-platform/reference/messenger-profile-api/
    #===========================================================================
    def set_account_linking_url(self, account_linking_url):
        """ Set Messenger's Account Linking to link user accounts in your bot to the user's Messenger account. 
        https://developers.facebook.com/docs/messenger-platform/reference/messenger-profile-api/account-linking-url
        """
        return self.send_configuration(**{'account_linking_url':account_linking_url})
    
    def set_get_started(self, get_started_payload):
        """ Set the welcome screen shown only the first time the user interacts with the Page on Messenger. 
        https://developers.facebook.com/docs/messenger-platform/reference/messenger-profile-api/get-started-button
        """
        return self.send_configuration(**{'get_started':get_started_payload})
    
    def set_greeting(self, greeting_payload):
        """ Set the greeting message people will see on the welcome screen of your bot. 
        https://developers.facebook.com/docs/messenger-platform/reference/messenger-profile-api/greeting
        """
        return self.send_configuration(**{'greeting':greeting_payload})
    
    def set_home_url(self, home_url_payload):
        """ Set home_url that allows your bot to enable a Chat Extension in the composer drawer in Messenger. 
        https://developers.facebook.com/docs/messenger-platform/reference/messenger-profile-api/home-url
        """
        return self.send_configuration(**{'home_url':home_url_payload})
    
    def set_persistent_menu(self, persistent_menu_payload):
        """ Set the persistent menu for your bot to help people discover and more easily 
        access your functionality throughout the conversation.
        https://developers.facebook.com/docs/messenger-platform/reference/messenger-profile-api/persistent-menu
        """
        for payload_entry in persistent_menu_payload:
            if (not payload_entry.get('composer_input_disabled',False)
                    and not payload_entry.get('call_to_actions',[])):
                raise Exception("call_to_actions is required if composer_input_disabled == True!")
        return self.send_configuration(**{'persistent_menu':persistent_menu_payload})
    
    def set_target_audience(self, target_audience_payload):
        """ Target Audience allows you to customize the audience that will see your bot in the Discover tab on Messenger. 
        https://developers.facebook.com/docs/messenger-platform/reference/messenger-profile-api/greeting
        """
        return self.send_configuration(**{'target_audience':target_audience_payload})
    
    def set_whitelisted_domains(self, whitelisted_domains):
        """ Set a list of third-party domains that are accessible in the Messenger webview for use with the Messenger Extensions SDK, and for the checkbox plugin.
        https://developers.facebook.com/docs/messenger-platform/reference/messenger-profile-api/domain-whitelisting
        """
        if whitelisted_domains is not None:
            if whitelisted_domains != '' and not isinstance(whitelisted_domains, (list)):
                whitelisted_domains = [whitelisted_domains]
        else:
            raise Exception("Domains non setted!")
        return self.send_configuration(**{'whitelisted_domains':whitelisted_domains})
    
    def add_domains_to_whitelist(self, domains):
        warnings.warn("add_domains_to_whitelist is deprecated, please use set_whitelisted_domains")
        return self.set_whitelisted_domains(domains)
    
    def clear_configuration(self, fields=[]):
        configuration = {
            'fields':fields or ['whitelisted_domains', 'greeting',
                                'get_started', 'persistent_menu']
        }
        return self.send_configuration(**configuration)
    
    def send_configuration(self, **payload):
        """ Set Properties that define various aspects of the following Messenger Platform features
        https://developers.facebook.com/docs/messenger-platform/reference/messenger-profile-api
        """
        request_endpoint = '{0}/me/messenger_profile'.format(self.graph_url)
        if self.log_request:
            print("request_endpoint : {0}".format(request_endpoint))
            print("params : {0}".format(payload))
        response = requests.post(
            request_endpoint,
            params=self.auth_args,
            json=payload
        )
        result = response.json()
        error = result.get('error',{})
        if error:
            print("Error! : {0}".format(error.get("message",'Facebook Error')))
        if self.log_response:
            print("result : {0}".format(result))
        return result
    
    def get_configuration(self, fields=[]):
        """ Set Properties that define various aspects of the following Messenger Platform features
        https://developers.facebook.com/docs/messenger-platform/reference/messenger-profile-api
        """
        if not fields:
            fields = ['account_linking_url','persistent_menu','get_started',
                      'greeting','whitelisted_domains','payment_settings',
                      'target_audience','home_url']
        params = self.auth_args
        params.update({
            'fields':",".join(list(fields))
        })
        request_endpoint = '{0}/me/messenger_profile'.format(self.graph_url)
        if self.log_request:
            print("request_endpoint : {0}".format(request_endpoint))
            print("params : {0}".format(params))
        response = requests.get(
            request_endpoint,
            params=self.auth_args,
            #json=payload
        )
        result = response.json()
        return result

    #===========================================================================
    # Section - Profile Data - 
    #===========================================================================
    
    def get_user_info(self, recipient_id, fields=None):
        """Getting information about the user
        https://developers.facebook.com/docs/messenger-platform/user-profile
        Input:
          recipient_id: recipient id to send to
        Output:
          Response from API as <dict>
        """
        params = {}
        if fields is not None and isinstance(fields, (list, tuple)):
            params['fields'] = ",".join(fields)

        params.update(self.auth_args)

        request_endpoint = '{0}/{1}'.format(self.graph_url, recipient_id)
        response = requests.get(request_endpoint, params=params)
        if response.status_code == 200:
            return response.json()

        return None
    
    #===========================================================================
    # Section - Send Message - 
    #===========================================================================
    def send_recipient(self,
                       recipient_id,
                       payload,
                       notification_type=NotificationType.regular,
                       do_send=True):
        payload['recipient'] = {'id': recipient_id}
        if six.PY2:
            payload['notification_type'] = notification_type
        else:
            payload['notification_type'] = notification_type.value
        if do_send:
            return self.send_raw(payload)
        else:
            return payload

    def send_message(self,
                     recipient_id,
                     message,
                     notification_type=NotificationType.regular,
                     do_send=True):
        return self.send_recipient(recipient_id, {'message': message},
                                   notification_type,
                                   do_send=do_send)

    def send_attachment(self,
                        recipient_id,
                        attachment_type,
                        attachment_path,
                        notification_type=NotificationType.regular,
                        do_send=True):
        """Send an attachment to the specified recipient using local path.
        Input:
            recipient_id: recipient id to send to
            attachment_type: type of attachment (image, video, audio, file)
            attachment_path: Path of attachment
        Output:
            Response from API as <dict>
        """
        with open(attachment_path, 'rb') as f:
            attachment_filename = os.path.basename(attachment_path)
            if attachment_type != 'file':
                attachment_ext = attachment_filename.split('.')[1]
                content_type = attachment_type + '/' + attachment_ext # eg: audio/mp3
            else:
                content_type = ''
            payload = {
                'recipient': json.dumps({
                    'id': recipient_id
                }),
                'notification_type': notification_type.value,
                'message': json.dumps({
                    'attachment': {
                        'type': attachment_type,
                        'payload': {}
                    }
                }),
                'filedata':
                (attachment_filename, f, content_type)
            }
            if do_send:
                multipart_data = MultipartEncoder(payload)
                multipart_header = {'Content-Type': multipart_data.content_type}
                request_endpoint = '{0}/me/messages'.format(self.graph_url)
                return requests.post(
                    request_endpoint,
                    data=multipart_data,
                    params=self.auth_args,
                    headers=multipart_header).json()
            else:
                return payload

    def send_attachment_url(self,
                            recipient_id,
                            attachment_type,
                            attachment_url,
                            notification_type=NotificationType.regular,
                            do_send=True):
        """Send an attachment to the specified recipient using URL.
        Input:
            recipient_id: recipient id to send to
            attachment_type: type of attachment (image, video, audio, file)
            attachment_url: URL of attachment
        Output:
            Response from API as <dict>
        """
        return self.send_message(recipient_id, {
            'attachment': {
                'type': attachment_type,
                'payload': {
                    'url': attachment_url
                }
            }
        }, notification_type, do_send=do_send)

    def send_text_message(self,
                          recipient_id,
                          message,
                          notification_type=NotificationType.regular,
                          do_send=True):
        """Send text messages to the specified recipient.
        https://developers.facebook.com/docs/messenger-platform/send-api-reference/text-message
        Input:
            recipient_id: recipient id to send to
            message: message to send
        Output:
            Response from API as <dict>
        """
        return self.send_message(recipient_id, {'text': message},
                                 notification_type,
                                 do_send=do_send)

    def send_generic_message(self,
                             recipient_id,
                             elements,
                             image_aspect_ratio='horizontal',
                             notification_type=NotificationType.regular,
                             do_send=True):
        """Send generic messages to the specified recipient.
        https://developers.facebook.com/docs/messenger-platform/send-api-reference/generic-template
        Input:
            recipient_id: recipient id to send to
            elements: generic message elements to send
            image_aspect_ratio: 'horizontal' (default) or 'square'
        Output:
            Response from API as <dict>
        """
        return self.send_message(recipient_id, {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "generic",
                    "image_aspect_ratio": image_aspect_ratio,
                    "elements": elements
                }
            }
        }, notification_type, do_send=do_send)
    
    def send_quick_reply(self,
                         recipient_id,
                         message,
                         buttons,
                         notification_type=NotificationType.regular,
                         do_send=True):
        """Quick Replies provide a way to present buttons in a message.
        https://developers.facebook.com/docs/messenger-platform/send-messages/quick-replies
        Input:
            recipient_id: recipient id to send to
            message: message to send
            buttons: buttons to send
        Output:
            Response from API as <dict>
        """
        return self.send_message(recipient_id, {
                'text': str(message),
                'quick_replies': buttons
                }, notification_type, do_send=do_send)
    
    def send_button_message(self,
                            recipient_id,
                            text,
                            buttons,
                            notification_type=NotificationType.regular,
                            do_send=True):
        """Send text messages to the specified recipient.
        https://developers.facebook.com/docs/messenger-platform/send-api-reference/button-template
        Input:
            recipient_id: recipient id to send to
            text: text of message to send
            buttons: buttons to send
        Output:
            Response from API as <dict>
        """
        return self.send_message(recipient_id, {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "button",
                    "text": text,
                    "buttons": buttons
                }
            }
        }, notification_type, do_send=do_send)

    def send_action(self,
                    recipient_id,
                    action,
                    notification_type=NotificationType.regular,
                    do_send=True):
        """Send typing indicators or send read receipts to the specified recipient.
        https://developers.facebook.com/docs/messenger-platform/send-api-reference/sender-actions

        Input:
            recipient_id: recipient id to send to
            action: action type (mark_seen, typing_on, typing_off)
        Output:
            Response from API as <dict>
        """
        return self.send_recipient(recipient_id, {'sender_action': action},
                                   notification_type, do_send=do_send)

    def send_image(self,
                   recipient_id,
                   image_path,
                   notification_type=NotificationType.regular,
                   do_send=True):
        """Send an image to the specified recipient.
        Image must be PNG or JPEG or GIF (more might be supported).
        https://developers.facebook.com/docs/messenger-platform/send-api-reference/image-attachment
        Input:
            recipient_id: recipient id to send to
            image_path: path to image to be sent
        Output:
            Response from API as <dict>
        """
        return self.send_attachment(recipient_id, "image", image_path,
                                    notification_type, do_send=do_send)

    def send_image_url(self,
                       recipient_id,
                       image_url,
                       notification_type=NotificationType.regular,
                       do_send=True):
        """Send an image to specified recipient using URL.
        Image must be PNG or JPEG or GIF (more might be supported).
        https://developers.facebook.com/docs/messenger-platform/send-api-reference/image-attachment
        Input:
            recipient_id: recipient id to send to
            image_url: url of image to be sent
        Output:
            Response from API as <dict>
        """
        return self.send_attachment_url(recipient_id, "image", image_url,
                                        notification_type, do_send=do_send)

    def send_audio(self,
                   recipient_id,
                   audio_path,
                   notification_type=NotificationType.regular,
                   do_send=True):
        """Send audio to the specified recipient.
        Audio must be MP3 or WAV
        https://developers.facebook.com/docs/messenger-platform/send-api-reference/audio-attachment
        Input:
            recipient_id: recipient id to send to
            audio_path: path to audio to be sent
        Output:
            Response from API as <dict>
        """
        return self.send_attachment(recipient_id, "audio", audio_path,
                                    notification_type, do_send=do_send)

    def send_audio_url(self,
                       recipient_id,
                       audio_url,
                       notification_type=NotificationType.regular,
                       do_send=True):
        """Send audio to specified recipient using URL.
        Audio must be MP3 or WAV
        https://developers.facebook.com/docs/messenger-platform/send-api-reference/audio-attachment
        Input:
            recipient_id: recipient id to send to
            audio_url: url of audio to be sent
        Output:
            Response from API as <dict>
        """
        return self.send_attachment_url(recipient_id, "audio", audio_url,
                                        notification_type, do_send=do_send)

    def send_video(self,
                   recipient_id,
                   video_path,
                   notification_type=NotificationType.regular,
                   do_send=True):
        """Send video to the specified recipient.
        Video should be MP4 or MOV, but supports more (https://www.facebook.com/help/218673814818907).
        https://developers.facebook.com/docs/messenger-platform/send-api-reference/video-attachment
        Input:
            recipient_id: recipient id to send to
            video_path: path to video to be sent
        Output:
            Response from API as <dict>
        """
        return self.send_attachment(recipient_id, "video", video_path,
                                    notification_type, do_send=do_send)

    def send_video_url(self,
                       recipient_id,
                       video_url,
                       notification_type=NotificationType.regular, 
                       do_send=True):
        """Send video to specified recipient using URL.
        Video should be MP4 or MOV, but supports more (https://www.facebook.com/help/218673814818907).
        https://developers.facebook.com/docs/messenger-platform/send-api-reference/video-attachment
        Input:
            recipient_id: recipient id to send to
            video_url: url of video to be sent
        Output:
            Response from API as <dict>
        """
        return self.send_attachment_url(recipient_id, "video", video_url,
                                        notification_type, do_send=do_send)

    def send_file(self,
                  recipient_id,
                  file_path,
                  notification_type=NotificationType.regular,
                  do_send=True):
        """Send file to the specified recipient.
        https://developers.facebook.com/docs/messenger-platform/send-api-reference/file-attachment
        Input:
            recipient_id: recipient id to send to
            file_path: path to file to be sent
        Output:
            Response from API as <dict>
        """
        return self.send_attachment(recipient_id, "file", file_path,
                                    notification_type, do_send=do_send)

    def send_file_url(self,
                      recipient_id,
                      file_url,
                      notification_type=NotificationType.regular, 
                       do_send=True):
        """Send file to the specified recipient.
        https://developers.facebook.com/docs/messenger-platform/send-api-reference/file-attachment
        Input:
            recipient_id: recipient id to send to
            file_url: url of file to be sent
        Output:
            Response from API as <dict>
        """
        return self.send_attachment_url(recipient_id, "file", file_url,
                                        notification_type, do_send=do_send)

    def _get_error_params(self, error_obj):
        error_params = {}
        error_fields = ['message', 'code', 'error_subcode', 'error_user_msg',
                        'is_transient', 'error_data', 'error_user_title',
                        'fbtrace_id']
        if 'error' in error_obj:
            error_obj = error_obj['error']
        for field in error_fields:
            error_params[field] = error_obj.get(field)
        return error_params
    
    def send_raw(self, payload):
        """
        @TODO Myabe Use facepy.graph_api.GraphAPI for exceptions handler and other shortcuts, 
              and to have an always update service.. if so `auth_args` will be unuseful
        """
        request_endpoint = '{0}/me/messages'.format(self.graph_url)
        #=======================================================================
        # if FACEPY_ENABLED:
        #     from facepy.graph_api import GraphAPI
        #     graph = GraphAPI(self.access_token,appsecret=self.app_secret)
        #     request_data = graph.post(request_endpoint, payload)
        #=======================================================================
        request_data = json.dumps(payload, cls=AttrsEncoder)
        if self.log_request:
            print("request data to {0}: {1} "
                  "".format(request_endpoint,
                            request_data))
        response = requests.post(
            request_endpoint,
            params=self.auth_args,
            data=json.dumps(payload, cls=AttrsEncoder),
            headers={'Content-Type': 'application/json'})
        data = response.json()
        if self.raise_exception:
            #ERROR Raise
            if type(data) is dict:
                if 'error' in data:
                    error = data['error']
                    print("error: {0}".format(error))
                    if error.get('type') == "OAuthException":
                        raise OAuthError(**self._get_error_params(data))
                    else:
                        raise FacebookError(**self._get_error_params(data))
                # Facebook occasionally reports errors in its legacy error format.
                if 'error_msg' in data:
                    error_msg = data['error_msg']
                    print("error_msg: {0}".format(error_msg))
                    raise FacebookError(**self._get_error_params(data))
            if self.log_response:
                print("response data: {0}".format(data))
        return data

    def _send_payload(self, payload):
        """ Deprecated, use send_raw instead """
        return self.send_raw(payload)


    ####################################
    ###  HANDOVER PROTOCOL
    ##########################
    def pass_thread_control(self, recipient_id,
                            target_app_id=263902037430900,  # Page inbox
                            help_message="Pass to Secondary Receiver"):
        """
        See  https://developers.facebook.com/docs/messenger-platform/reference/handover-protocol/pass-thread-control

        :param recipient_id: PSID of Faceboook user
        :param target_app_id: Facebook APP ID
        :param help_message: String to pass to secondary receiver app
        :return:

        """
        payload = {
            "recipient": {"id": recipient_id},
            "target_app_id": target_app_id,
            "metadata": help_message,
        }
        """
        https://developers.facebook.com/docs/messenger-platform/reference/handover-protocol/pass-thread-control

        @TODO Myabe Use facepy.graph_api.GraphAPI for exceptions handler and other shortcuts,
              and to have an always update service.. if so `auth_args` will be unuseful
        """
        request_endpoint = '{0}/me/pass_thread_control'.format(self.graph_url)
        #=======================================================================
        # if FACEPY_ENABLED:
        #     from facepy.graph_api import GraphAPI
        #     graph = GraphAPI(self.access_token,appsecret=self.app_secret)
        #     request_data = graph.post(request_endpoint, payload)
        #=======================================================================
        request_data = json.dumps(payload, cls=AttrsEncoder)
        if self.log_request:
            print("request data to {0}: {1} "
                  "".format(request_endpoint,
                            request_data))
        response = requests.post(
            request_endpoint,
            params=self.auth_args,
            data=json.dumps(payload, cls=AttrsEncoder),
            headers={'Content-Type': 'application/json'})
        data = response.json()
        if self.raise_exception:
            #ERROR Raise
            if type(data) is dict:
                if 'error' in data:
                    error = data['error']
                    print("error: {0}".format(error))
                    if error.get('type') == "OAuthException":
                        raise OAuthError(**self._get_error_params(data))
                    else:
                        raise FacebookError(**self._get_error_params(data))
                # Facebook occasionally reports errors in its legacy error format.
                if 'error_msg' in data:
                    error_msg = data['error_msg']
                    print("error_msg: {0}".format(error_msg))
                    raise FacebookError(**self._get_error_params(data))
            if self.log_response:
                print("response data: {0}".format(data))
        return data

    def take_thread_control(self, recipient_id, message=""):
        """
        See  https://developers.facebook.com/docs/messenger-platform/reference/handover-protocol/pass-thread-control

        :param recipient_id: PSID of Faceboook user
        :param message: String to pass to secondary receiver app
        :return: 

        """
        payload = {
            "recipient": {"id": recipient_id},
            "metadata": message,
        }
        """
        https://developers.facebook.com/docs/messenger-platform/reference/handover-protocol/pass-thread-control

        @TODO Myabe Use facepy.graph_api.GraphAPI for exceptions handler and other shortcuts,
              and to have an always update service.. if so `auth_args` will be unuseful
        """
        request_endpoint = '{0}/me/take_thread_control'.format(self.graph_url)
        #=======================================================================
        # if FACEPY_ENABLED:
        #     from facepy.graph_api import GraphAPI
        #     graph = GraphAPI(self.access_token,appsecret=self.app_secret)
        #     request_data = graph.post(request_endpoint, payload)
        #=======================================================================
        request_data = json.dumps(payload, cls=AttrsEncoder)
        if self.log_request:
            print("request data to {0}: {1} "
                  "".format(request_endpoint,
                            request_data))
        response = requests.post(
            request_endpoint,
            params=self.auth_args,
            data=json.dumps(payload, cls=AttrsEncoder),
            headers={'Content-Type': 'application/json'})
        data = response.json()
        if self.raise_exception:
            #ERROR Raise
            if type(data) is dict:
                if 'error' in data:
                    error = data['error']
                    print("error: {0}".format(error))
                    if error.get('type') == "OAuthException":
                        raise OAuthError(**self._get_error_params(data))
                    else:
                        raise FacebookError(**self._get_error_params(data))
                # Facebook occasionally reports errors in its legacy error format.
                if 'error_msg' in data:
                    error_msg = data['error_msg']
                    print("error_msg: {0}".format(error_msg))
                    raise FacebookError(**self._get_error_params(data))
            if self.log_response:
                print("response data: {0}".format(data))
        return data