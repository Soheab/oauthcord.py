:layout: default
:description: Separate reference pages for every internal payload and TypedDict module.

Types
=====

This section documents the internal payload aliases and ``TypedDict`` modules in
``oauthcord.internals._types``.
Each page focuses on one module so related request and response shapes stay grouped and
easy to browse.

.. toctree::
   :maxdepth: 2
   :caption: Core

   base
   token
   current_auth_info

.. toctree::
   :maxdepth: 1
   :caption: Identity and Relationships

   user
   member
   guild
   connections
   relationship
   invite

.. toctree::
   :maxdepth: 1
   :caption: Applications and Store

   application
   entitlement
   store

.. toctree::
   :maxdepth: 1
   :caption: Messaging and Interaction

   attachment
   channels
   message
   commands
   components

.. toctree::
   :maxdepth: 1
   :caption: Real-time and Social

   lobby
