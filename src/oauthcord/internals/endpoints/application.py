from typing import TYPE_CHECKING

import aiohttp

from ...utils import NotSet
from .base import BaseHTTPClient, Route

if TYPE_CHECKING:
    from ...models.file import File
    from .._types import (
        application as application_types,
    )
    from .._types import (
        entitlement as entitlement_types,
    )
    from .base import ValidToken


class ApplicationHTTPClientMixin(BaseHTTPClient):
    """Mixin for application-related HTTP methods."""

    async def create_application_attachment(
        self,
        token: ValidToken,
        *,
        application_id: int | str,
        file: File,
    ) -> application_types.CreateApplicationAttachmentResponse:
        form = aiohttp.FormData()
        form.add_field(
            "file",
            file.read(),
            filename=file.filename,
            content_type=file.content_type,
        )
        return await self.request(
            Route("POST", f"/applications/{application_id}/attachment"),
            token=token,
            data=form,
        )

    async def get_partial_application(
        self,
        token: ValidToken,
        *,
        application_id: int | str,
    ) -> application_types.PartialApplicationResponse:
        return await self.request(
            Route("GET", f"/applications/{application_id}/partial"),
            token=token,
        )

    async def get_user_application_role_connection(
        self,
        token: ValidToken,
        *,
        application_id: int | str,
    ) -> application_types.ApplicationRoleConnectionResponse:
        return await self.request(
            Route("GET", f"/users/@me/applications/{application_id}/role-connection"),
            token=token,
        )

    async def edit_user_application_role_connection(
        self,
        token: ValidToken,
        *,
        application_id: int | str,
        platform_name: str | None = NotSet,
        platform_username: str | None = NotSet,
        metadata: dict[str, str] | None = NotSet,
    ) -> application_types.ApplicationRoleConnectionResponse:
        data: application_types.ModifyUserApplicationRoleConnectionRequest = {}
        if platform_name is not NotSet:
            data["platform_name"] = platform_name
        if platform_username is not NotSet:
            data["platform_username"] = platform_username
        if metadata is not NotSet:
            data["metadata"] = metadata

        return await self.request(
            Route("PUT", f"/users/@me/applications/{application_id}/role-connection"),
            token=token,
            json=data,
        )

    async def create_application_quick_link(
        self,
        token: ValidToken,
        *,
        application_id: int | str,
        title: str,
        description: str,
        image: File,
        custom_id: str | None = None,
    ) -> application_types.ActivityLinkResponse:
        data: application_types.CreateApplicationQuickLinkRequest = {
            "title": title,
            "description": description,
            "image": image.to_data_uri(),
        }
        if custom_id is not None:
            data["custom_id"] = custom_id

        return await self.request(
            Route("POST", f"/applications/{application_id}/quick-links/"),
            token=token,
            json=data,
        )

    async def get_bulk_application_identities(
        self,
        token: ValidToken,
        *,
        user_ids: list[int | str],
    ) -> application_types.GetBulkApplicationIdentitiesResponse:
        data: application_types.GetBulkApplicationIdentitiesRequest = {
            "user_ids": user_ids
        }
        return await self.request(
            Route("POST", "/application-identities"),
            token=token,
            json=data,
        )

    async def get_application_entitlements(
        self,
        token: ValidToken,
        *,
        application_id: int | str,
        user_id: int | str | None = None,
        sku_ids: list[int | str] | None = None,
        guild_id: int | str | None = None,
        exclude_ended: bool | None = None,
        exclude_deleted: bool | None = None,
        before: int | str | None = None,
        after: int | str | None = None,
        limit: int | None = None,
    ) -> entitlement_types.GetApplicationEntitlementsResponse:
        params: entitlement_types.GetApplicationEntitlementsRequest = {}
        if user_id is not None:
            params["user_id"] = user_id
        if sku_ids is not None:
            params["sku_ids"] = sku_ids
        if guild_id is not None:
            params["guild_id"] = guild_id
        if exclude_ended is not None:
            params["exclude_ended"] = exclude_ended
        if exclude_deleted is not None:
            params["exclude_deleted"] = exclude_deleted
        if before is not None:
            params["before"] = before
        if after is not None:
            params["after"] = after
        if limit is not None:
            params["limit"] = limit

        return await self.request(
            Route("GET", f"/applications/{application_id}/entitlements"),
            token=token,
            params=params,
        )

    async def get_application_entitlement(
        self,
        token: ValidToken,
        *,
        application_id: int | str,
        entitlement_id: int | str,
    ) -> entitlement_types.EntitlementResponse:
        return await self.request(
            Route(
                "GET", f"/applications/{application_id}/entitlements/{entitlement_id}"
            ),
            token=token,
        )

    async def consume_application_entitlement(
        self,
        token: ValidToken,
        *,
        application_id: int | str,
        entitlement_id: int | str,
    ) -> None:
        await self.request(
            Route(
                "POST",
                f"/applications/{application_id}/entitlements/{entitlement_id}/consume",
            ),
            token=token,
        )

    async def delete_application_entitlement(
        self,
        token: ValidToken,
        *,
        application_id: int | str,
        entitlement_id: int | str,
    ) -> None:
        await self.request(
            Route(
                "DELETE",
                f"/applications/{application_id}/entitlements/{entitlement_id}",
            ),
            token=token,
        )
