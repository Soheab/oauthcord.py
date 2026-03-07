from collections.abc import Sequence
from typing import TYPE_CHECKING, override

from ..utils import _serialize_localizations, convert_snowflake
from ._base import BaseModel, StatelessBaseModel
from .enums import (
    ApplicationCommandHandlerType,
    ApplicationCommandOptionType,
    ApplicationCommandPermissionType,
    ApplicationCommandType,
    ChannelType,
    IntegrationInstallType,
    InteractionContextType,
    Locale,
    to_enum,
)
from .flags import Permissions

if TYPE_CHECKING:
    from .internals._types import commands
    from .internals.http import OAuth2HTTPClient

__all__ = (
    "ApplicationCommandPermission",
    "Command",
    "Group",
    "GuildApplicationCommandPermissions",
    "Option",
    "OptionChoice",
    "RequestCommand",
    "Subcommand",
)


class OptionChoice(
    StatelessBaseModel[
        "commands._StringApplicationCommandOptionChoiceResponse | commands.ApplicationCommandOptionChoiceRequest",
    ]
):
    __slots__ = ("name", "name_localizations", "value")

    @override
    def _initialize(
        self,
        data: commands.ApplicationCommandOptionChoiceResponse
        | commands.ApplicationCommandOptionChoiceRequest,
    ) -> None:
        self.name: str = data["name"]
        self.name_localizations: dict[Locale, str] = (
            {to_enum(Locale, k): v for k, v in nl.items()}
            if (nl := data.get("name_localizations"))
            else {}
        )
        self.value: str | int | float = data["value"]

    @override
    def _to_request(self) -> commands.ApplicationCommandOptionChoiceRequest:  # pyright: ignore[reportIncompatibleMethodOverride]
        payload: commands.ApplicationCommandOptionChoiceRequest = {
            "name": self.name,
            "value": self.value,
        }
        if self.name_localizations:
            payload["name_localizations"] = _serialize_localizations(
                self.name_localizations
            )
        return payload


class Option(
    StatelessBaseModel[
        "commands.ApplicationCommandOptionResponse | commands.ApplicationCommandOptionRequest",
    ]
):
    __slots__ = (
        "autocomplete",
        "channel_types",
        "choices",
        "description",
        "description_localizations",
        "max_length",
        "max_value",
        "min_length",
        "min_value",
        "name",
        "name_localizations",
        "options",
        "required",
        "type",
    )

    @override
    def _initialize(
        self,
        data: commands.ApplicationCommandOptionResponse
        | commands.ApplicationCommandOptionRequest,
    ) -> None:
        if (option_type := data.get("type")) is None:
            raise ValueError("Option type is required.")
        if (name := data.get("name")) is None:
            raise ValueError("Option name is required.")
        if (description := data.get("description")) is None:
            raise ValueError("Option description is required.")

        self.type: ApplicationCommandOptionType = to_enum(
            ApplicationCommandOptionType, option_type
        )
        self.name: str = name
        self.description: str = description
        self.name_localizations: dict[Locale, str] | None = (
            {to_enum(Locale, k): v for k, v in nl.items()}
            if "name_localizations" in data
            and (nl := data["name_localizations"]) is not None
            else None
        )
        self.description_localizations: dict[Locale, str] | None = (
            {to_enum(Locale, k): v for k, v in dl.items()}
            if "description_localizations" in data
            and (dl := data["description_localizations"]) is not None
            else None
        )

        self.required: bool | None = data.get("required", None)
        self.choices: list[OptionChoice] | None = (
            [
                self._initialize_subclass(OptionChoice, choice)
                for choice in data["choices"]
            ]
            if "choices" in data
            else None
        )
        self.options: list[Option] | None = (
            [self._initialize_subclass(Option, option) for option in data["options"]]
            if "options" in data
            else None
        )

        self.min_value: int | float | None = data.get("min_value", None)
        self.max_value: int | float | None = data.get("max_value", None)
        self.min_length: int | None = data.get("min_length", None)
        self.max_length: int | None = data.get("max_length", None)
        self.autocomplete: bool | None = data.get("autocomplete", None)
        self.channel_types: list[ChannelType] | None = (
            [to_enum(ChannelType, ct) for ct in data["channel_types"]]
            if "channel_types" in data
            else None
        )

    @override
    def _to_request(self) -> commands.ApplicationCommandOptionRequest:  # pyright: ignore[reportIncompatibleMethodOverride]
        payload: commands.ApplicationCommandOptionRequest = {
            "type": self.type.value,
            "name": self.name,
            "description": self.description,
        }

        if self.name_localizations is not None:
            payload["name_localizations"] = _serialize_localizations(
                self.name_localizations
            )
        if self.description_localizations is not None:
            payload["description_localizations"] = _serialize_localizations(
                self.description_localizations
            )
        if self.required is not None:
            payload["required"] = self.required
        if self.choices is not None:
            payload["choices"] = [choice._to_request() for choice in self.choices]
        if self.min_value is not None:
            payload["min_value"] = self.min_value
        if self.max_value is not None:
            payload["max_value"] = self.max_value
        if self.min_length is not None:
            payload["min_length"] = self.min_length
        if self.max_length is not None:
            payload["max_length"] = self.max_length
        if self.autocomplete is not None:
            payload["autocomplete"] = self.autocomplete
        if self.channel_types is not None:
            payload["channel_types"] = [
                channel_type.value for channel_type in self.channel_types
            ]
        if self.options is not None:
            payload["options"] = [option._to_request() for option in self.options]

        return payload


class RequestCommand(StatelessBaseModel["commands.ApplicationCommandRequest"]):
    __slots__ = (
        "contexts",
        "default_member_permissions",
        "description",
        "description_localizations",
        "handler",
        "integration_types",
        "name",
        "name_localizations",
        "nsfw",
        "options",
        "type",
    )

    @override
    def _initialize(self, data: commands.ApplicationCommandRequest) -> None:
        self.type: ApplicationCommandType = to_enum(
            ApplicationCommandType, data.get("type", 1)
        )
        self.name: str = data["name"]
        self.description: str | None = data.get("description")
        self.name_localizations: dict[Locale, str] | None = (
            {to_enum(Locale, k): v for k, v in nl.items()}
            if (nl := data.get("name_localizations"))
            else None
        )
        self.description_localizations: dict[Locale, str] | None = (
            {to_enum(Locale, k): v for k, v in dl.items()}
            if (dl := data.get("description_localizations"))
            else None
        )
        self.contexts: list[InteractionContextType] | None = (
            [to_enum(InteractionContextType, context) for context in contexts]
            if (contexts := data.get("contexts")) is not None
            else None
        )
        self.integration_types: list[IntegrationInstallType] | None = (
            [
                to_enum(IntegrationInstallType, install_type)
                for install_type in integration_types
            ]
            if (integration_types := data.get("integration_types")) is not None
            else None
        )
        self.default_member_permissions: Permissions | None = (
            Permissions(int(permission_bits))
            if (permission_bits := data.get("default_member_permissions"))
            else None
        )
        self.nsfw: bool | None = data.get("nsfw")
        self.handler: ApplicationCommandHandlerType | None = (
            to_enum(ApplicationCommandHandlerType, handler)
            if (handler := data.get("handler")) is not None
            else None
        )
        self.options: list[Option] | None = (
            [self._initialize_subclass(Option, option) for option in options]
            if (options := data.get("options")) is not None
            else None
        )

    @override
    def _to_request(self) -> commands.ApplicationCommandRequest:  # pyright: ignore[reportIncompatibleMethodOverride]
        payload: commands.ApplicationCommandRequest = {
            "type": self.type.value,
            "name": self.name,
            "description": self.description or "...",
        }
        if self.description is not None:
            payload["description"] = self.description
        if self.name_localizations is not None:
            payload["name_localizations"] = _serialize_localizations(
                self.name_localizations
            )
        if self.description_localizations is not None:
            payload["description_localizations"] = _serialize_localizations(
                self.description_localizations
            )
        if self.contexts is not None:
            payload["contexts"] = [context.value for context in self.contexts]
        if self.integration_types is not None:
            payload["integration_types"] = [
                install_type.value for install_type in self.integration_types
            ]
        if self.default_member_permissions is not None:
            payload["default_member_permissions"] = str(
                self.default_member_permissions.value
            )
        if self.nsfw is not None:
            payload["nsfw"] = self.nsfw
        if self.handler is not None:
            payload["handler"] = self.handler.value
        if self.options is not None:
            payload["options"] = [option._to_request() for option in self.options]
        return payload


class Command[
    D = commands.ApplicationCommandResponse | commands.GuildApplicationCommandResponse
](BaseModel[D]):
    __slots__ = (
        "application_id",
        "contexts",
        "default_member_permissions",
        "description",
        "description_localizations",
        "guild_id",
        "id",
        "integration_types",
        "name",
        "name_localizations",
        "nsfw",
        "options",
        "type",
        "version",
    )

    @override
    def _initialize(self, data: D) -> None:
        data_: (
            commands.ApplicationCommandResponse
            | commands.GuildApplicationCommandResponse
        ) = data  # type: ignore
        self.type: ApplicationCommandType = to_enum(
            ApplicationCommandType, data_.get("type", 1)
        )
        self.id: int = convert_snowflake(data_, "id")
        self.application_id: int = convert_snowflake(data_, "application_id")
        self.name: str = data_["name"]
        self.description: str | None = data_.get("description")
        self.contexts: list[InteractionContextType] = [
            to_enum(InteractionContextType, ctx) for ctx in data_.get("contexts", [])
        ]
        self.integration_types: list[IntegrationInstallType] = [
            to_enum(IntegrationInstallType, it)
            for it in data_.get("integration_types", [])
        ]
        self.default_member_permissions: Permissions | None = (
            Permissions(int(dmp))
            if (dmp := data_.get("default_member_permissions"))
            else None
        )
        self.nsfw: bool = data_.get("nsfw", False)
        self.version: int = convert_snowflake(data_, "version")
        self.name_localizations: dict[Locale, str] | None = (
            {to_enum(Locale, k): v for k, v in nl.items()}
            if (nl := data_.get("name_localizations"))
            else None
        )
        self.description_localizations: dict[Locale, str] | None = (
            {to_enum(Locale, k): v for k, v in dl.items()}
            if (dl := data_.get("description_localizations"))
            else None
        )

        self.guild_id: int | None = convert_snowflake(
            data_, "guild_id", always_available=False
        )

        self.options: list[Option] = [
            self._initialize_subclass(Option, option)
            for option in data_.get("options", [])
        ]


class Subcommand[D = commands._SubCommandCommandOptionResponse](BaseModel[D]):
    __slots__ = (
        "description",
        "description_localizations",
        "name",
        "name_localizations",
        "options",
        "parent",
        "type",
    )

    def __init__(
        self,
        *,
        http: OAuth2HTTPClient,
        parent: Group,
        data: D,
    ) -> None:
        super().__init__(http=http, data=data)
        self.parent: Group = parent

    @override
    def _initialize(self, data: D) -> None:
        data_: commands._SubCommandCommandOptionResponse = data  # type: ignore
        self.type: ApplicationCommandOptionType = to_enum(
            ApplicationCommandOptionType, data_["type"]
        )
        self.name: str = data_["name"]
        self.description: str = data_["description"]
        self.name_localizations: dict[Locale, str] | None = (
            {to_enum(Locale, k): v for k, v in nl.items()}
            if (nl := data_.get("name_localizations"))
            else None
        )
        self.description_localizations: dict[Locale, str] | None = (
            {to_enum(Locale, k): v for k, v in dl.items()}
            if (dl := data_.get("description_localizations"))
            else None
        )

        self.options: list[Option] = [
            self._initialize_subclass(Option, option)
            for option in data_.get("options", [])
        ]


class Group(
    Command[
        "commands.ApplicationCommandResponse | commands.GuildApplicationCommandResponse"
    ],
):
    __slots__ = ("commands",)

    def __init__(
        self,
        *,
        http: OAuth2HTTPClient,
        command: commands.ApplicationCommandResponse
        | commands.GuildApplicationCommandResponse,
        data: commands._SubCommandGroupCommandOptionResponse,
    ) -> None:
        super().__init__(http=http, data=command)
        self.commands: list[Subcommand] = [
            Subcommand(http=self._http, parent=self, data=option_data)
            for option_data in data.get("options", [])
        ]


class ApplicationCommandPermission(
    BaseModel["commands.ApplicationCommandPermissionsResponse"]
):
    __slots__ = ("id", "permission", "type")

    @override
    def _initialize(self, data: commands.ApplicationCommandPermissionsResponse) -> None:
        self.id: int = convert_snowflake(data, "id")
        self.type: ApplicationCommandPermissionType = to_enum(
            ApplicationCommandPermissionType, data["type"]
        )
        self.permission: bool = data["permission"]


class GuildApplicationCommandPermissions(
    BaseModel["commands.GuildApplicationCommandPermissionsResponse"]
):
    __slots__ = ("application_id", "guild_id", "id", "permissions")

    @override
    def _initialize(
        self, data: commands.GuildApplicationCommandPermissionsResponse
    ) -> None:
        self.id: int = convert_snowflake(data, "id")
        self.application_id: int = convert_snowflake(data, "application_id")
        self.guild_id: int = convert_snowflake(data, "guild_id")
        self.permissions: list[ApplicationCommandPermission] = [
            self._initialize_subclass_with_http(ApplicationCommandPermission, perm)
            for perm in data["permissions"]
        ]


def _data_to_obj(  # pyright: ignore[reportUnusedFunction]
    http: OAuth2HTTPClient,
    data: list[commands.ApplicationCommandResponse],
) -> list[Command | Group]:
    res: list[Command | Group] = []
    for d in data:
        options: Sequence[commands.ApplicationCommandOptionResponse] = d.get(
            "options", []
        )
        if not options or d.get("type", 1) != 1:
            res.append(Command(http=http, data=d))
            continue

        created_group = False
        for option in options:
            if option["type"] == 2:
                res.append(Group(http=http, command=d, data=option))
                created_group = True

        if not created_group:
            res.append(Command(http=http, data=d))

    return res
