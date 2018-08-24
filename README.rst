pymessenger2 |Build Status|
===========================

Python Wrapper for `Facebook Messenger
Platform <https://developers.facebook.com/docs/messenger-platform>`__.

**Disclaimer**: This wrapper is **NOT** an official wrapper and do not
attempt to represent Facebook in anyway.

About
~~~~~

This wrapper has the following functions:

Send Message:

-  ``send_text_message(recipient_id, message)``
-  ``send_message(recipient_id, message)``
-  ``send_generic_message(recipient_id, elements)``
-  ``send_button_message(recipient_id, text, buttons)``
-  ``send_quick_reply(recipient_id, text, buttons)``
-  ``send_attachment(recipient_id, attachment_type, attachment_path)``
-  ``send_attachment_url(recipient_id, attachment_type, attachment_url)``
-  ``send_image(recipient_id, image_path)``
-  ``send_image_url(recipient_id, image_url)``
-  ``send_audio(recipient_id, audio_path)``
-  ``send_audio_url(recipient_id, audio_url)``
-  ``send_video(recipient_id, video_path)``
-  ``send_video_url(recipient_id, video_url)``
-  ``send_file(recipient_id, file_path)``
-  ``send_file_url(recipient_id, file_url)``
-  ``send_action(recipient_id, action)``
-  ``send_raw(payload)``

Profile Data:

-  ``get_user_info(recipient_id)``

Configurations:

-  ``set_get_started(payload)``
-  ``set_greeting(payload)``
-  ``set_home_url(payload)``
-  ``set_persistent_menu(payload)``
-  ``set_target_audience(payload)``
-  ``set_whitelisted_domains(payload)``
-  ``add_domains_to_whitelist(payload)``
-  ``send_configuration(payload)``
-  ``get_configuration()``
-  ``clear_configuration(**payload)``

Handover Protocol: 

<https://developers.facebook.com/docs/messenger-platform/handover-protocol>

- ``pass_thread_control(recipient_id, target_app_id, help_message)``
- ``take_thread_control(recipient_id, message)``

You can see the code/documentation for there in
`bot.py <pymessenger/bot.py>`__.

The functions return the full JSON body of the actual API call to
Facebook.

Register for an Access Token
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You'll need to setup a `Facebook
App <https://developers.facebook.com/apps/>`__, Facebook Page, get the
Page Access Token and link the App to the Page before you can really
start to use the Send/Receive service.

`This quickstart guide should
help <https://developers.facebook.com/docs/messenger-platform/quickstart>`__

Installation
~~~~~~~~~~~~

.. code:: bash

    pip install pymessenger2

Usage
~~~~~

.. code:: python

    from pymessenger2.bot import Bot

    bot = Bot(<access_token>, [optional: app_secret])
    bot.send_text_message(recipient_id, message)

**Note**: From Facebook regarding User IDs

    These ids are page-scoped. These ids differ from those returned from
    Facebook Login apps which are app-scoped. You must use ids retrieved
    from a Messenger integration for this page in order to function
    properly.

    If ``app_secret`` is initialized, an app\_secret\_proof will be
    generated and send with every request. Appsecret Proofs helps
    further secure your client access tokens. You can find out more on
    the `Facebook
    Docs <https://developers.facebook.com/docs/graph-api/securing-requests#appsecret_proof>`__

Sending a generic template message:
'''''''''''''''''''''''''''''''''''

    `Generic Template
    Messages <https://developers.facebook.com/docs/messenger-platform/implementation#receive_message>`__
    allows you to add cool elements like images, text all in a single
    bubble.

.. code:: python

    from pymessenger2.bot import Bot
    from pymessenger2 import Element
    bot = Bot(<access_token>)
    elements = []
    element = Element(title="test", image_url="<arsenal_logo.png>", subtitle="subtitle", item_url="http://arsenal.com")
    elements.append(element)

    bot.send_generic_message(recipient_id, elements)

Output:

.. figure:: https://cloud.githubusercontent.com/assets/68039/14519266/4c7033b2-0250-11e6-81a3-f85f3809d86c.png
   :alt: Generic Bot Output

   Generic Bot Output

Sending an image/video/file using an URL:
'''''''''''''''''''''''''''''''''''''''''

.. code:: python

    from pymessenger2.bot import Bot
    bot = Bot(<access_token>)
    image_url = "http://url/to/image.png"
    bot.send_image_url(recipient_id, image_url)


ChatBot Configuration:
'''''''''''''''''''''''''''''''''''

    `Messenger Profile API <https://developers.facebook.com/docs/messenger-platform/reference/messenger-profile-api/>`__
    allows you to manage congigurations like Persistent Menu, Whitelisted Domain, ecc.

.. code:: python

    from pymessenger2.bot import Bot
    bot = Bot(<access_token>)
    bot.set_get_started({"payload":"Hello Friend"})
    bot.set_whitelisted_domains(["https://www.mywebsite.it",
                                 "https://katesapp.ngrok.io"])
    bot.set_greeting([
          {
            "locale":"default",
            "text":"Hello!"
          }, {
            "locale":"en_US",
            "text":"Hi"
          }, {
            "locale":"it_IT",
            "text":"Ciao"
          }
    ])
    bot.set_persistent_menu([{
          "locale":"default",
          "composer_input_disabled": False,
          "call_to_actions":[
            {
              "title":"🍽 Recipes",
              "type":"nested",
              "call_to_actions":[
                {
                  "title":"🐟 Fish Recipes",
                  "type":"postback",
                  "payload":"FISH-RECIPES"
                },
                {
                  "title":"🍖 Meat Recipes",
                  "type":"postback",
                  "payload":"MEAT-RECIPES"
                },
                {
                  "title":"🍱 Japanese Recipes",
                  "type":"postback",
                  "payload":"JAPAN-RECIPES"
                },
                {
                  "title":"🍆 Vegan Recipes",
                  "type":"postback",
                  "payload":"VEGAN-RECIPES"
                },
              ]
            },{
              "title":"🔔 Notifications",
              "type":"postback",
              "payload":"NOTIFICATIONS"
            }
          ]
        }])
    bot.get_configuration()
                                      
Output:

.. figure:: https://user-images.githubusercontent.com/2088831/41346006-895817ee-6f05-11e8-9048-f9a06df3f727.png
   :alt: Persistent Menu
.. figure:: https://user-images.githubusercontent.com/2088831/41345991-8111431c-6f05-11e8-9d09-40df3a2a60be.png
   :alt: Persistent Menu

   {'data': [{'persistent_menu': [{
          "locale":"default",
          "composer_input_disabled": False,
          "call_to_actions":[
            {
              "title":"🍽 Recipes",
              "type":"nested",
              "call_to_actions":[
                {
                  "title":"🐟 Fish Recipes",
                  "type":"postback",
                  "payload":"FISH-RECIPES"
                },
                {
                  "title":"🍖 Meat Recipes",
                  "type":"postback",
                  "payload":"MEAT-RECIPES"
                },
                {
                  "title":"🍱 Japanese Recipes",
                  "type":"postback",
                  "payload":"JAPAN-RECIPES"
                },
                {
                  "title":"🍆 Vegan Recipes",
                  "type":"postback",
                  "payload":"VEGAN-RECIPES"
                },
              ]
            },{
              "title":"🔔 Notifications",
              "type":"postback",
              "payload":"NOTIFICATIONS"
            }
          ]
        }],
        'get_started': {'payload': 'Ciao'}, 
        'greeting': [
            {'locale': 'default', 'text': 'Hello!'}, 
            {'locale': 'en_US', 'text': 'Hi'}, 
            {'locale': 'it_IT', 'text': 'Ciao'}
        ], 
        'whitelisted_domains': ["https://www.mywebsite.it",
                                 "https://katesapp.ngrok.io"]}]}

Integration with DialogFlow:
'''''''''''''''''''''''''''''''''''
If you want to use DialogFlow for your bot and customize Facebook return messages, you can use our Bot.

.. code:: python

from pymessenger2.bot import Bot


class MyDialogFlowWebhook(generic.View):
  
    def is_facebook_request(self, request_data):
        return request_data.get('originalDetectIntentRequest',{}).get('source','') == 'facebook'

    def post(self, request, *args, **kwargs):
        request_data = json.loads(request.body)
        logger.debug("DialogFlow Webhook - Handling POST event\n"
                     "data: {0}".format(data))
        
        ...  
        
        query_result=request_data.get('queryResult',{})
        response_data = {
            'fulfillmentText':query_result.get('fulfillmentText'),
            'fulfillmentMessages':query_result.get('fulfillmentMessages'),
            'payload':query_result.get('originalDetectIntentRequest',{}).get('payload',{}),
            'outputContexts':query_result.get('outputContexts'),
            'source':"dialogflow-webhook",
            
        }
        
        ...

        if self.is_facebook_request(request_data):
            recipient_id = request_data.get('originalDetectIntentRequest',{}).get('payload',{}).get('data',{}).get('sender',{}).get('id',None)
            dialogflow_action = query_result.get('action', "")
            if dialogflow_action == "SAY HELLO":
                chatbot = Bot(<YOUR_PAGE_ACCESS_TOKEN>,
                              raise_exception=True)
                bot_response_payload = chatbot.send_text_message(recipient_id=recipient_id,
                                                             message="Hi guy, I'm here!!!",
                                                             do_send=False)
                response_data['payload'].update({
                    "facebook": [
                        bot_response_payload['message']
                    ]
                })
        return response_data



Todo
~~~~
'''''''''''''''''''''''''''''''''''
-  Structured Messages
-  Use Facepy?
-  Receipt Messages
-  Airlines
-  Tests!
-  More examples
-  Documentation about handover protocol

Example
~~~~~~~

.. figure:: https://cloud.githubusercontent.com/assets/68039/14516627/905c84ae-0237-11e6-918e-2c2ae9352f7d.png
   :alt: Screenshot of Echo Facebook Bot

   Screenshot of Echo Facebook Bot

You can find an example of an Echo Facebook Bot in ``examples/``

.. |Build Status| image:: https://travis-ci.org/Cretezy/pymessenger2.svg?branch=master
   :target: https://travis-ci.org/Cretezy/pymessenger2
