from typing import TYPE_CHECKING

from ..file import File

if TYPE_CHECKING:
    from ..application import (
        ActivityLink,
        ApplicationRoleConnection,
        PartialApplication,
    )
    from ..attachment import Attachment
    from .http import OAuth2HTTPClient, ValidToken


class ApplicationHTTPMixin:
    id: int
    _http: OAuth2HTTPClient

    async def create_attachment(self, token: ValidToken, *, file: File) -> Attachment:
        return await self._http.__get_client().create_application_attachment(
            token=token, application_id=self.id, file=file
        )

    async def get_partial(self, *, token: ValidToken) -> PartialApplication:
        return await self._http.__get_client().partial_application(
            token=token, application_id=self.id
        )

    async def get_user_role_connection(
        self, token: ValidToken
    ) -> ApplicationRoleConnection:
        return await self._http.__get_client().user_application_role_connection(
            token=token,
            application_id=self.id,
        )

    async def edit_user_role_connection(
        self,
        *,
        token: ValidToken,
        platform_name: str | None = None,
        platform_username: str | None = None,
        metadata: dict[str, str] | None = None,
    ) -> ApplicationRoleConnection:
        return await self._http.__get_client().edit_user_application_role_connection(
            token=token,
            application_id=self.id,
            platform_name=platform_name,
            platform_username=platform_username,
            metadata=metadata,
        )

    async def create_quick_link(
        self,
        token: ValidToken,
        *,
        description: str,
        image: File,
        title: str,
        custom_id: str | None = None,
    ) -> ActivityLink:
        return await self._http.__get_client().create_application_quick_link(
            token=token,
            application_id=self.id,
            description=description,
            image=image,
            title=title,
            custom_id=custom_id,
        )
