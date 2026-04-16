.. currentmodule:: oauthcord

:layout: landing
:hide_breadcrumbs: true
:content_max_width: 1180px
:description: Reference documentation for oauthcord.py, a typed async wrapper for Discord OAuth2.

oauthcord.py Documentation
==========================

.. container:: doc-hero

   oauthcord.py is a focused async wrapper for Discord's OAuth2 and user-authorised REST
   APIs. Start with :class:`Client` to create authorization URLs and exchange codes, then
   use :class:`AuthorisedSession` to call Discord with typed models instead of raw JSON.

.. container:: buttons

   :doc:`Read the Client Reference <client>`
   :doc:`Browse All Models <models/_index>`
   :doc:`Inspect Types <types/_index>`
   `View on GitHub <https://github.com/Soheab/oauthcord.py>`_

.. grid:: 1 1 3 3
   :gutter: 3

   .. grid-item-card:: OAuth2-first
      :class-card: feature-card sd-shadow-sm

      Built for the parts of Discord you reach through user authorization, token exchange,
      refresh, revoke, and OAuth-scoped API calls.

   .. grid-item-card:: Typed throughout
      :class-card: feature-card sd-shadow-sm

      Public models, enums, payloads, and utilities stay aligned so the wrapper is easier
      to read, autocomplete, and type-check.

   .. grid-item-card:: Async by default
      :class-card: feature-card sd-shadow-sm

      The transport is based on :mod:`aiohttp`, so the wrapper fits naturally into modern
      async web apps and callback handlers.

Start Here
----------

.. grid:: 1 2 2 3
   :gutter: 3

   .. grid-item-card:: Client
      :link: client
      :link-type: doc
      :class-card: feature-card sd-shadow-sm

      The public entry point for authorization URLs, token exchange, refresh, revoke, and
      authorised sessions.

   .. grid-item-card:: Builders
      :link: builders
      :link-type: doc
      :class-card: feature-card sd-shadow-sm

      Helper classes for constructing structured request payloads for commands, polls,
      and similar API shapes.

   .. grid-item-card:: Models
      :link: models/_index
      :link-type: doc
      :class-card: feature-card sd-shadow-sm

      Separate pages for every public model module so related classes stay grouped and
      easy to scan.

   .. grid-item-card:: Enums
      :link: enums/_index
      :link-type: doc
      :class-card: feature-card sd-shadow-sm

      Grouped enum reference for OAuth scopes, store values, channels, invites, and the
      rest of the serialized API surface.

   .. grid-item-card:: Errors and Utils
      :link: errors
      :link-type: doc
      :class-card: feature-card sd-shadow-sm

      Shared exceptions and helper functions used across parsing, conversion, and request
      handling.

   .. grid-item-card:: Internals
      :link: types/_index
      :link-type: doc
      :class-card: feature-card sd-shadow-sm

      Internal payload and type definitions for contributors who need the raw request and
      response structures used under the public API.

Typical Flow
------------

1. Create a :class:`Client` with your application ID, client secret, redirect URI, and requested scopes.
2. Send the user to :meth:`Client.get_authorization_url`.
3. Exchange the returned code with :meth:`Client.exchange_token`.
4. Use the resulting :class:`AuthorisedSession` for user-authorised Discord requests.

Quick Example
-------------

.. code-block:: python

   from oauthcord import Client, Scope

   client = Client(
       client_id=123456789012345678,
       client_secret="your-client-secret",
       redirect_uri="http://127.0.0.1:8000/callback",
       scopes=[Scope.IDENTIFY, Scope.GUILDS],
   )

   authorize_url = client.get_authorization_url()
   session = await client.exchange_token(code)
   user = await session.current_user()

.. toctree::
   :hidden:
   :maxdepth: 2

   client
   builders
   enums/_index
   errors
   utils
   types/_index
   models/_index
