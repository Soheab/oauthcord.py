"""
The MIT License (MIT)

Copyright (c) 2015-present Rapptz

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

from typing import (
    Literal,
    NotRequired,
    Required,
    TypedDict,
)

from .base import InteractionContextType, Locale, Snowflake
from .channels import ChannelType

ApplicationCommandType = Literal[1, 2, 3, 4]
ApplicationCommandOptionType = Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
ApplicationIntegrationType = Literal[0, 1]
EntryPointCommandHandlerType = Literal[1, 2]


class ApplicationCommandOptionChoiceRequest(TypedDict):
    name: str
    value: str | int | float
    name_localizations: NotRequired[dict[str, str]]


class ApplicationCommandOptionRequest(TypedDict, total=False):
    type: ApplicationCommandOptionType
    name: str
    description: str
    name_localizations: NotRequired[dict[str, str]]
    description_localizations: NotRequired[dict[str, str]]
    required: bool
    choices: list[ApplicationCommandOptionChoiceRequest]
    min_value: int | float
    max_value: int | float
    min_length: int
    max_length: int
    autocomplete: bool
    channel_types: list[int]
    options: list[ApplicationCommandOptionRequest]


_ValueApplicationCommandOptionRequest = ApplicationCommandOptionRequest
_SubCommandCommandOptionRequest = ApplicationCommandOptionRequest
_SubCommandGroupCommandOptionRequest = ApplicationCommandOptionRequest


class _BaseApplicationCommandRequest(TypedDict, total=False):
    type: Required[ApplicationCommandType]
    name: Required[str]
    name_localizations: dict[str, str]
    description: Required[str]
    description_localizations: dict[str, str]
    options: list[ApplicationCommandOptionRequest]
    contexts: list[InteractionContextType]
    integration_types: list[ApplicationIntegrationType]
    default_member_permissions: str | None
    nsfw: bool
    handler: int


_ChatInputApplicationCommandRequest = _BaseApplicationCommandRequest
_UserApplicationCommandRequest = _BaseApplicationCommandRequest
_MessageApplicationCommandRequest = _BaseApplicationCommandRequest
_PrimaryEntryPointApplicationCommandRequest = _BaseApplicationCommandRequest


ApplicationCommandRequest = _BaseApplicationCommandRequest


class _BaseApplicationCommandOptionResponse(TypedDict):
    name: str
    description: str
    name_localizations: NotRequired[dict[Locale, str] | None]
    description_localizations: NotRequired[dict[Locale, str] | None]


class _SubCommandCommandOptionResponse(_BaseApplicationCommandOptionResponse):
    type: Literal[1]
    options: list[_ValueApplicationCommandOptionResponse]


class _SubCommandGroupCommandOptionResponse(_BaseApplicationCommandOptionResponse):
    type: Literal[2]
    options: list[_SubCommandCommandOptionResponse]


class _BaseValueApplicationCommandOptionResponse(
    _BaseApplicationCommandOptionResponse, total=False
):
    required: bool


class _StringApplicationCommandOptionChoiceResponse(TypedDict):
    name: str
    name_localizations: NotRequired[dict[Locale, str] | None]
    value: str


class _StringApplicationCommandOptionResponse(_BaseApplicationCommandOptionResponse):
    type: Literal[3]
    choices: NotRequired[list[_StringApplicationCommandOptionChoiceResponse]]
    min_length: NotRequired[int]
    max_length: NotRequired[int]
    autocomplete: NotRequired[bool]


class _IntegerApplicationCommandOptionChoiceResponse(TypedDict):
    name: str
    name_localizations: NotRequired[dict[Locale, str] | None]
    value: int


class _IntegerApplicationCommandOptionResponse(
    _BaseApplicationCommandOptionResponse, total=False
):
    type: Required[Literal[4]]
    min_value: int
    max_value: int
    choices: list[_IntegerApplicationCommandOptionChoiceResponse]
    autocomplete: bool


class _BooleanApplicationCommandOptionResponse(
    _BaseValueApplicationCommandOptionResponse
):
    type: Literal[5]


class _ChannelApplicationCommandOptionChoiceResponse(
    _BaseApplicationCommandOptionResponse
):
    type: Literal[7]
    channel_types: NotRequired[list[ChannelType]]


class _NonChannelSnowflakeApplicationCommandOptionChoiceResponse(
    _BaseValueApplicationCommandOptionResponse
):
    type: Literal[6, 8, 9, 11]


_SnowflakeApplicationCommandOptionChoiceResponse = (
    _ChannelApplicationCommandOptionChoiceResponse
    | _NonChannelSnowflakeApplicationCommandOptionChoiceResponse
)


class _NumberApplicationCommandOptionChoiceResponse(TypedDict):
    name: str
    name_localizations: NotRequired[dict[Locale, str] | None]
    value: float


class _NumberApplicationCommandOptionResponse(
    _BaseValueApplicationCommandOptionResponse, total=False
):
    type: Required[Literal[10]]
    min_value: float
    max_value: float
    choices: list[_NumberApplicationCommandOptionChoiceResponse]
    autocomplete: bool


_ValueApplicationCommandOptionResponse = (
    _StringApplicationCommandOptionResponse
    | _IntegerApplicationCommandOptionResponse
    | _BooleanApplicationCommandOptionResponse
    | _SnowflakeApplicationCommandOptionChoiceResponse
    | _NumberApplicationCommandOptionResponse
)

ApplicationCommandOptionResponse = (
    _SubCommandGroupCommandOptionResponse
    | _SubCommandCommandOptionResponse
    | _ValueApplicationCommandOptionResponse
)

ApplicationCommandOptionChoiceResponse = (
    _StringApplicationCommandOptionChoiceResponse
    | _IntegerApplicationCommandOptionChoiceResponse
    | _NumberApplicationCommandOptionChoiceResponse
)


class _BaseApplicationCommandResponse(TypedDict):
    id: Snowflake
    application_id: Snowflake
    name: str
    contexts: list[InteractionContextType]
    integration_types: list[ApplicationIntegrationType]
    default_member_permissions: NotRequired[str | None]
    nsfw: NotRequired[bool]
    version: Snowflake
    name_localizations: NotRequired[dict[Locale, str] | None]
    description_localizations: NotRequired[dict[Locale, str] | None]


class _ChatInputApplicationCommandResponse(
    _BaseApplicationCommandResponse, total=False
):
    description: Required[str]
    type: Literal[1]
    options: (
        list[_ValueApplicationCommandOptionResponse]
        | list[_SubCommandCommandOptionResponse | _SubCommandGroupCommandOptionResponse]
    )


class _PrimaryEntryPointApplicationCommandResponse(_BaseApplicationCommandResponse):
    description: Required[str]
    type: Literal[4]
    handler: EntryPointCommandHandlerType


class _BaseContextMenuApplicationCommandResponse(_BaseApplicationCommandResponse):
    description: Literal[""]


class _UserApplicationCommandResponse(_BaseContextMenuApplicationCommandResponse):
    type: Literal[2]


class _MessageApplicationCommandResponse(_BaseContextMenuApplicationCommandResponse):
    type: Literal[3]


GlobalApplicationCommandResponse = (
    _ChatInputApplicationCommandResponse
    | _UserApplicationCommandResponse
    | _MessageApplicationCommandResponse
    | _PrimaryEntryPointApplicationCommandResponse
)


class _GuildChatInputApplicationCommandResponse(_ChatInputApplicationCommandResponse):
    guild_id: Snowflake


class _GuildUserApplicationCommandResponse(_UserApplicationCommandResponse):
    guild_id: Snowflake


class _GuildMessageApplicationCommandResponse(_MessageApplicationCommandResponse):
    guild_id: Snowflake


GuildApplicationCommandResponse = (
    _GuildChatInputApplicationCommandResponse
    | _GuildUserApplicationCommandResponse
    | _GuildMessageApplicationCommandResponse
)


ApplicationCommandResponse = (
    GlobalApplicationCommandResponse | GuildApplicationCommandResponse
)


ApplicationCommandPermissionType = Literal[1, 2, 3]


class ApplicationCommandPermissionsResponse(TypedDict):
    id: Snowflake
    type: ApplicationCommandPermissionType
    permission: bool


class GuildApplicationCommandPermissionsResponse(TypedDict):
    id: Snowflake
    application_id: Snowflake
    guild_id: Snowflake
    permissions: list[ApplicationCommandPermissionsResponse]
