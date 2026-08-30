from __future__ import annotations

from typing import override

from ...internals._types.rpc import application
from ...models._base import BaseModel

__all__ = ("Ticket",)


class Ticket(
    BaseModel[
        application.GetEntitlementTicketResponse
        | application.GetApplicationTicketResponse
        | application.RequestProxyTicketRefreshResponse
    ]
):
    __slots__ = ("ticket",)

    @override
    def _initialize(
        self,
        data: application.GetEntitlementTicketResponse
        | application.GetApplicationTicketResponse
        | application.RequestProxyTicketRefreshResponse,
    ) -> None:
        self.ticket: str = data["ticket"]
