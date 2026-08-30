"""Command types for the application and monetization RPC commands.

Covers ``VALIDATE_APPLICATION``, the ticket commands, and the purchase / SKU /
entitlement commands.

See https://docs.discord.food/topics/rpc#validate-application.
"""

from __future__ import annotations

from typing import NotRequired, TypedDict

from ..base import Snowflake
from ..entitlement import EntitlementResponse
from ..store import SKU

# Responds with null if the user is entitled to the application's primary SKU.
ValidateApplicationResponse = None


class GetEntitlementTicketResponse(TypedDict):
    ticket: str


class GetApplicationTicketResponse(TypedDict):
    ticket: str


class StartPurchaseRequest(TypedDict):
    sku_id: Snowflake
    pid: NotRequired[int]


StartPurchaseResponse = list[EntitlementResponse]


class StartPremiumPurchaseRequest(TypedDict):
    pid: NotRequired[int]


StartPremiumPurchaseResponse = None  # undocumented
GetSKUsResponse = list[SKU]
GetEntitlementsResponse = list[EntitlementResponse]


class GetSKUsEmbeddedResponse(TypedDict):
    skus: list[SKU]


class GetEntitlementsEmbeddedResponse(TypedDict):
    entitlements: list[EntitlementResponse]


class RequestProxyTicketRefreshResponse(TypedDict):
    ticket: str
