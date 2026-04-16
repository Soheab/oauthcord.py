:layout: default
:description: Public client API for authorization URLs, token exchange, and authorised sessions.

Client
======

The client layer is the main public entry point for the OAuth2 flow.

Use :class:`oauthcord.Client` to build the authorization flow and exchange tokens. Use
:class:`oauthcord.AuthorisedSession` to call Discord on behalf of the authorised user
after the token exchange succeeds.

Client
-------

.. autoclass:: oauthcord.Client
   :members:
   :exclude-members: http

AuthorisedSession
------------------

.. autoclass:: oauthcord.AuthorisedSession
   :members:
   :exclude-members: client, token
   :inherited-members:
   :show-inheritance: