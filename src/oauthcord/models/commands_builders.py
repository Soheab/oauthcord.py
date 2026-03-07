from reprlib import recursive_repr
from typing import TYPE_CHECKING, Self

from ..utils import _serialize_localizations
from . import commands as command_models
from .enums import (
    ApplicationCommandHandlerType,
    ApplicationCommandOptionType,
    ApplicationCommandType,
    ChannelType,
    IntegrationInstallType,
    InteractionContextType,
    Locale,
)
from .flags import Permissions

if TYPE_CHECKING:
    from .internals._types import commands as command_types


__all__ = (
    "ChatInputCommandBuilder",
    "ChatInputGroupCommandBuilder",
    "ChatInputSubCommandBuilder",
    "MessageCommandBuilder",
    "OptionBuilder",
    "OptionChoiceBuilder",
    "PrimaryEntryPointCommandBuilder",
    "UserCommandBuilder",
)


class WithContextsMixin:
    def __init__(
        self,
        *,
        integration_types: list[IntegrationInstallType] | None = None,
        contexts: list[InteractionContextType] | None = None,
    ) -> None:
        self.integration_types: list[IntegrationInstallType] | None = integration_types
        self.contexts: list[InteractionContextType] | None = contexts


class WithOptionsMixin:
    def __init__(self, *, options: list[OptionBuilder] | None = None) -> None:
        self.options: list[OptionBuilder] = options or []

    def append_option(self, option: OptionBuilder) -> Self:
        self.options.append(option)
        return self

    def add_option(
        self,
        *,
        type: ApplicationCommandOptionType,
        name: str,
        description: str,
        name_localizations: dict[Locale, str] | None = None,
        description_localizations: dict[Locale, str] | None = None,
        required: bool = False,
        max_value: float | None = None,
        min_value: float | None = None,
        min_length: int | None = None,
        max_length: int | None = None,
        autocomplete: bool = False,
        channel_types: list[ChannelType] | None = None,
        choices: list[OptionChoiceBuilder] | None = None,
    ) -> Self:
        if type in (
            ApplicationCommandOptionType.SUB_COMMAND,
            ApplicationCommandOptionType.SUB_COMMAND_GROUP,
        ):
            raise ValueError(
                "Option type cannot be SUB_COMMAND or SUB_COMMAND_GROUP. Use ChatInputSubCommandBuilder or ChatInputGroupCommandBuilder instead."
            )
        option = OptionBuilder(
            type=type,
            name=name,
            description=description,
            name_localizations=name_localizations,
            description_localizations=description_localizations,
            required=required,
            max_value=max_value,
            min_value=min_value,
            min_length=min_length,
            max_length=max_length,
            autocomplete=autocomplete,
            channel_types=channel_types,
            choices=choices,
        )
        return self.append_option(option)


class WithNameLocalizationsMixin:
    def __init__(self, *, name_localizations: dict[Locale, str] | None = None) -> None:
        if name_localizations is not None:
            if not isinstance(name_localizations, dict):
                raise ValueError(
                    "name_localizations must be a dictionary mapping Locale to str."
                )

            if not all(isinstance(locale, Locale) for locale in name_localizations):
                raise ValueError(
                    "All keys in name_localizations must be instances of the Locale enum."
                )

            if not all(
                isinstance(localized_name, str)
                for localized_name in (name_localizations).values()
            ):
                raise ValueError("All values in name_localizations must be strings.")
        self.name_localizations: dict[Locale, str] = name_localizations or {}

    def add_name_localization(self, locale: Locale, localized_name: str) -> Self:
        if not isinstance(locale, Locale):
            msg = "Locale must be an instance of the Locale enum."
            raise TypeError(msg)

        if not isinstance(localized_name, str):
            msg = "Localized name must be a string."
            raise TypeError(msg)

        self.name_localizations[locale] = localized_name
        return self


class WithDescriptionLocalizationsMixin:
    def __init__(
        self, *, description_localizations: dict[Locale, str] | None = None
    ) -> None:
        if description_localizations is not None:
            if not isinstance(description_localizations, dict):
                raise ValueError(
                    "description_localizations must be a dictionary mapping Locale to str."
                )

            if not all(
                isinstance(locale, Locale) for locale in description_localizations
            ):
                msg = "All keys in description_localizations must be instances of the Locale enum."
                raise TypeError(msg)

            if not all(
                isinstance(localized_description, str)
                for localized_description in (description_localizations).values()
            ):
                msg = "All values in description_localizations must be strings."
                raise TypeError(msg)

        self.description_localizations: dict[Locale, str] = (
            description_localizations or {}
        )

    def add_description_localization(
        self, locale: Locale, localized_description: str
    ) -> Self:
        if not isinstance(locale, Locale):
            msg = "Locale must be an instance of the Locale enum."
            raise TypeError(msg)

        if not isinstance(localized_description, str):
            msg = "Localized description must be a string."
            raise TypeError(msg)

        self.description_localizations[locale] = localized_description
        return self


class OptionChoiceBuilder(WithNameLocalizationsMixin):
    def __init__(
        self,
        *,
        name: str,
        value: str | float,
        name_localizations: dict[Locale, str] | None = None,
    ) -> None:
        super().__init__(name_localizations=name_localizations)
        self.name: str = name
        self.value: str | int | float = value

    def to_request(self) -> command_types.ApplicationCommandOptionChoiceRequest:
        model_data: command_types.ApplicationCommandOptionChoiceRequest = {
            "name": self.name,
            "value": self.value,
        }
        if self.name_localizations:
            model_data["name_localizations"] = _serialize_localizations(
                self.name_localizations
            )
        return command_models.OptionChoice(data=model_data)._to_request()

    def __repr__(self) -> str:
        return f"<OptionChoiceBuilder name={self.name!r} value={self.value!r}>"


class OptionBuilder(WithNameLocalizationsMixin, WithDescriptionLocalizationsMixin):
    """Builder for application command options.

    .. warning::
        This does not represent subcommands or subcommand groups like the API. For those,
        use :class:`ChatInputSubCommandBuilder` and :class:`ChatInputGroupCommandBuilder`
        instead.

    Parameters
    ----------
    type: :class:`ApplicationCommandOptionType`
        The type of the option. Cannot be ``SUB_COMMAND`` or ``SUB_COMMAND_GROUP``.
    name: :class:`str`
        The name of the option.
    description: :class:`str`
        The description of the option.
    name_localizations: :class:`dict`\\[:class:`Locale`, :class:`str`\\] | None
        A dictionary mapping :class:`Locale` to localized name strings.

        You can also use :meth:`add_name_localization` to add entries to this dictionary.
    description_localizations: :class:`dict`\\[:class:`Locale`, :class:`str`\\] | None
        A dictionary mapping :class:`Locale` to localized description strings.
    required: :class:`bool`
        Whether this option is required. Defaults to ``False``.
    max_value: :class:`int` | :class:`float` | None
        The maximum value for ``INTEGER`` or ``NUMBER`` options.
    min_value: :class:`int` | :class:`float` | None
        The minimum value for ``INTEGER`` or ``NUMBER`` options.
    min_length: :class:`int` | None
        The minimum length for ``STRING`` options.
    max_length: :class:`int` | None
        The maximum length for ``STRING`` options.
    autocomplete: :class:`bool`
        Whether this option has autocomplete.

        This is mutually exclusive with choices, and can only be set
        for ``STRING``, ``INTEGER``, and ``NUMBER`` options.

        Defaults to ``False``.
    channel_types: :class:`list`\\[:class:`ChannelType`\\] | None
        The allowed channel types for ``CHANNEL`` options.

        You can also use :meth:`add_channel_type` to add channel types to this list.
    choices: :class:`list`\\[:class:`OptionChoiceBuilder`\\] | None
        A list of choices for this option.

        This is mutually exclusive with autocomplete, and can only be set
        for ``STRING``, ``INTEGER``, and ``NUMBER`` options.

        You can also use :meth:`add_choice` to add choices to this list.
    """

    def __init__(
        self,
        *,
        type: ApplicationCommandOptionType,
        name: str,
        description: str,
        name_localizations: dict[Locale, str] | None = None,
        description_localizations: dict[Locale, str] | None = None,
        required: bool = False,
        max_value: float | None = None,
        min_value: float | None = None,
        min_length: int | None = None,
        max_length: int | None = None,
        autocomplete: bool = False,
        channel_types: list[ChannelType] | None = None,
        choices: list[OptionChoiceBuilder] | None = None,
    ) -> None:
        if min_value is not None and max_value is not None:
            if type not in (
                ApplicationCommandOptionType.INTEGER,
                ApplicationCommandOptionType.NUMBER,
            ):
                msg = "min_value and max_value can only be set for INTEGER and NUMBER option types."
                raise TypeError(msg)
            if min_value > max_value:
                msg = "min_value cannot be greater than max_value."
                raise ValueError(msg)

        if min_length is not None and max_length is not None:
            if type != ApplicationCommandOptionType.STRING:
                msg = (
                    "min_length and max_length can only be set for STRING option types."
                )
                raise ValueError(msg)
            if min_length > max_length:
                msg = "min_length cannot be greater than max_length."
                raise ValueError(msg)

            if min_length < 1 or max_length > 4000:
                msg = (
                    "min_length must be at least 1 and max_length must not exceed 4000."
                )
                raise ValueError(msg)

        if choices and autocomplete:
            msg = "Options with choices cannot have autocomplete enabled."
            raise ValueError(msg)

        if choices or (
            autocomplete
            and type
            not in (
                ApplicationCommandOptionType.STRING,
                ApplicationCommandOptionType.INTEGER,
                ApplicationCommandOptionType.NUMBER,
            )
        ):
            msg = "Choices and autocomplete can only be set for STRING, INTEGER, and NUMBER option types."
            raise ValueError(msg)

        if channel_types and type is not ApplicationCommandOptionType.CHANNEL:
            msg = "channel_types can only be set for CHANNEL option types."
            raise ValueError(msg)

        if type in (
            ApplicationCommandOptionType.SUB_COMMAND,
            ApplicationCommandOptionType.SUB_COMMAND_GROUP,
        ):
            msg = "Option type cannot be SUB_COMMAND or SUB_COMMAND_GROUP. Use ChatInputSubCommandBuilder or ChatInputGroupCommandBuilder instead."
            raise ValueError(msg)

        WithNameLocalizationsMixin.__init__(self, name_localizations=name_localizations)
        WithDescriptionLocalizationsMixin.__init__(
            self, description_localizations=description_localizations
        )
        self.type: ApplicationCommandOptionType = type
        self.name: str = name
        self.description: str = description
        self.required: bool = required
        self.max_value: int | float | None = max_value
        self.min_value: int | float | None = min_value
        self.min_length: int | None = min_length
        self.max_length: int | None = max_length
        self.autocomplete: bool = autocomplete
        self.channel_types: list[ChannelType] | None = channel_types
        self.choices: list[OptionChoiceBuilder] | None = choices

    def add_choice(
        self,
        *,
        name: str,
        value: str | float,
        name_localizations: dict[Locale, str] | None = None,
    ) -> Self:
        if self.choices is None:
            self.choices = []

        choice = OptionChoiceBuilder(
            name=name,
            value=value,
            name_localizations=name_localizations,
        )
        self.choices.append(choice)
        return self

    def add_channel_type(self, channel_type: ChannelType) -> Self:
        if self.channel_types is None:
            self.channel_types = []
        self.channel_types.append(channel_type)
        return self

    def __repr__(self) -> str:
        return f"<OptionBuilder type={self.type!r} name={self.name!r}>"

    def to_request(self) -> command_types._ValueApplicationCommandOptionRequest:
        model_data: command_types.ApplicationCommandOptionRequest = {
            "type": self.type.value,
            "name": self.name,
            "description": self.description,
        }

        if self.name_localizations:
            model_data["name_localizations"] = _serialize_localizations(
                self.name_localizations
            )
        if self.description_localizations:
            model_data["description_localizations"] = _serialize_localizations(
                self.description_localizations
            )
        if self.required:
            model_data["required"] = self.required
        if self.max_value is not None:
            model_data["max_value"] = self.max_value
        if self.min_value is not None:
            model_data["min_value"] = self.min_value
        if self.min_length is not None:
            model_data["min_length"] = self.min_length
        if self.max_length is not None:
            model_data["max_length"] = self.max_length
        if self.autocomplete:
            model_data["autocomplete"] = self.autocomplete
        if self.channel_types is not None:
            model_data["channel_types"] = [
                channel_type.value for channel_type in self.channel_types
            ]
        if self.choices is not None:
            model_data["choices"] = [choice.to_request() for choice in self.choices]

        return command_models.Option(data=model_data)._to_request()


class _BaseApplicationCommandBuilder(WithNameLocalizationsMixin):
    def __init__(
        self,
        *,
        type: ApplicationCommandType,
        name: str,
        name_localizations: dict[Locale, str] | None = None,
    ) -> None:
        super().__init__(name_localizations=name_localizations)

        self.type: ApplicationCommandType = type
        self.name: str = name

    @recursive_repr()
    def __repr__(self) -> str:
        attrs = [
            f"type={self.type!r}",
            f"name={self.name!r}",
        ]
        for key, value in self.__dict__.items():
            if key not in {"type", "name", "groups", "subcommands"}:
                attrs.append(f"{key}={value!r}")

        return f"{self.__class__.__name__}({', '.join(attrs)})"


class _BaseChatInputCommandBuilder(
    _BaseApplicationCommandBuilder, WithOptionsMixin, WithDescriptionLocalizationsMixin
):
    def __init__(
        self,
        *,
        type: ApplicationCommandType,
        name: str,
        description: str,
        name_localizations: dict[Locale, str] | None = None,
        description_localizations: dict[Locale, str] | None = None,
        options: list[OptionBuilder] | None = None,
    ) -> None:
        super().__init__(
            type=type,
            name=name,
            name_localizations=name_localizations,
        )
        WithOptionsMixin.__init__(self, options=options)
        WithDescriptionLocalizationsMixin.__init__(
            self, description_localizations=description_localizations
        )

        self.description: str = description


class ChatInputCommandBuilder(_BaseChatInputCommandBuilder, WithContextsMixin):
    def __init__(
        self,
        *,
        name: str,
        description: str,
        name_localizations: dict[Locale, str] | None = None,
        description_localizations: dict[Locale, str] | None = None,
        options: list[OptionBuilder] | None = None,
        integration_types: list[IntegrationInstallType] | None = None,
        contexts: list[InteractionContextType] | None = None,
        default_member_permissions: Permissions | None = None,
        nsfw: bool = False,
    ) -> None:
        super().__init__(
            type=ApplicationCommandType.CHAT_INPUT,
            name=name,
            name_localizations=name_localizations,
            description=description,
            description_localizations=description_localizations,
            options=options,
        )
        WithContextsMixin.__init__(
            self,
            integration_types=integration_types,
            contexts=contexts,
        )
        self.default_member_permissions: Permissions | None = default_member_permissions
        self.nsfw: bool = nsfw

    def to_request(self) -> command_types._ChatInputApplicationCommandRequest:
        model_data: command_types.ApplicationCommandRequest = {
            "type": self.type.value,
            "name": self.name,
            "description": self.description,
        }

        if self.name_localizations:
            model_data["name_localizations"] = _serialize_localizations(
                self.name_localizations
            )
        if self.description_localizations:
            model_data["description_localizations"] = _serialize_localizations(
                self.description_localizations
            )
        if self.options:
            model_data["options"] = [option.to_request() for option in self.options]
        if self.integration_types is not None:
            model_data["integration_types"] = [
                integration_type.value for integration_type in self.integration_types
            ]
        if self.contexts is not None:
            model_data["contexts"] = [context.value for context in self.contexts]
        if self.default_member_permissions is not None:
            model_data["default_member_permissions"] = str(
                self.default_member_permissions.value
            )
        if self.nsfw:
            model_data["nsfw"] = self.nsfw

        return command_models.RequestCommand(data=model_data)._to_request()


class ChatInputSubCommandBuilder(_BaseChatInputCommandBuilder):
    def __init__(
        self,
        *,
        name: str,
        description: str,
        name_localizations: dict[Locale, str] | None = None,
        description_localizations: dict[Locale, str] | None = None,
        options: list[OptionBuilder] | None = None,
    ) -> None:
        super().__init__(
            type=ApplicationCommandType.CHAT_INPUT,
            name=name,
            description=description,
            name_localizations=name_localizations,
            description_localizations=description_localizations,
            options=options,
        )
        self.parent: ChatInputGroupCommandBuilder | None = None

    @property
    def contexts(self) -> list[InteractionContextType] | None:
        return self._get_root_group().contexts

    @property
    def integration_types(self) -> list[IntegrationInstallType] | None:
        return self._get_root_group().integration_types

    def _get_root_group(self) -> ChatInputGroupCommandBuilder:
        parent: ChatInputGroupCommandBuilder | None = self.parent
        while parent is not None and parent.parent is not None:
            parent = parent.parent
        if parent is None:
            raise ValueError("Subcommand is not attached to a root chat input group.")
        return parent

    def to_request(self) -> command_types._SubCommandCommandOptionRequest:
        model_data: command_types.ApplicationCommandOptionRequest = {
            "type": ApplicationCommandOptionType.SUB_COMMAND.value,
            "name": self.name,
            "description": self.description,
            "options": [option.to_request() for option in self.options],
        }
        if self.name_localizations:
            model_data["name_localizations"] = _serialize_localizations(
                self.name_localizations
            )
        if self.description_localizations:
            model_data["description_localizations"] = _serialize_localizations(
                self.description_localizations
            )
        return command_models.Option(data=model_data)._to_request()


class ChatInputGroupCommandBuilder(_BaseApplicationCommandBuilder):
    def __init__(
        self,
        *,
        name: str,
        description: str,
        name_localizations: dict[Locale, str] | None = None,
        description_localizations: dict[Locale, str] | None = None,
        integration_types: list[IntegrationInstallType] | None = None,
        contexts: list[InteractionContextType] | None = None,
        default_member_permissions: Permissions | None = None,
        nsfw: bool = False,
        groups: list[ChatInputGroupCommandBuilder] | None = None,
        subcommands: list[ChatInputSubCommandBuilder] | None = None,
    ) -> None:
        super().__init__(
            type=ApplicationCommandType.CHAT_INPUT,
            name=name,
            name_localizations=name_localizations,
        )
        self.description: str = description
        self.description_localizations: dict[Locale, str] | None = (
            description_localizations
        )
        self.parent: ChatInputGroupCommandBuilder | None = None
        self._integration_types: list[IntegrationInstallType] | None = integration_types
        self._contexts: list[InteractionContextType] | None = contexts
        self.default_member_permissions: Permissions | None = default_member_permissions
        self.nsfw: bool = nsfw
        self.groups: list[ChatInputGroupCommandBuilder] = groups or []
        self.subcommands: list[ChatInputSubCommandBuilder] = subcommands or []

        for group in self.groups:
            group.parent = self

        for subcommand in self.subcommands:
            subcommand.parent = self

    @property
    def contexts(self) -> list[InteractionContextType] | None:
        if self.parent is None:
            return self._contexts
        return self._get_root_group().contexts

    @property
    def integration_types(self) -> list[IntegrationInstallType] | None:
        if self.parent is None:
            return self._integration_types
        return self._get_root_group().integration_types

    def _get_root_group(self) -> ChatInputGroupCommandBuilder:
        root: ChatInputGroupCommandBuilder = self
        while root.parent is not None:
            root = root.parent
        return root

    def add_group(
        self,
        *,
        name: str,
        description: str,
        name_localizations: dict[Locale, str] | None = None,
        description_localizations: dict[Locale, str] | None = None,
        groups: list[ChatInputGroupCommandBuilder] | None = None,
        subcommands: list[ChatInputSubCommandBuilder] | None = None,
    ) -> ChatInputGroupCommandBuilder:
        group = ChatInputGroupCommandBuilder(
            name=name,
            description=description,
            name_localizations=name_localizations,
            description_localizations=description_localizations,
            integration_types=None,  # inherited from parent
            contexts=None,  # inherited from parent
            default_member_permissions=None,  # inherited from parent
            nsfw=False,  # inherited from parent
            groups=groups,
            subcommands=subcommands,
        )
        group.parent = self
        self.groups.append(group)
        return group

    def add_subcommand(
        self,
        *,
        name: str,
        description: str,
        name_localizations: dict[Locale, str] | None = None,
        description_localizations: dict[Locale, str] | None = None,
        options: list[OptionBuilder] | None = None,
    ) -> ChatInputSubCommandBuilder:
        command = ChatInputSubCommandBuilder(
            name=name,
            description=description,
            name_localizations=name_localizations,
            description_localizations=description_localizations,
            options=options,
        )
        command.parent = self
        self.subcommands.append(command)
        return command

    def to_request(
        self,
    ) -> (
        command_types._ChatInputApplicationCommandRequest
        | command_types._SubCommandGroupCommandOptionRequest
    ):
        if self.parent is None:
            model_data: command_types.ApplicationCommandRequest = {
                "type": self.type.value,
                "name": self.name,
                "description": self.description,
                "options": [group._to_option_request() for group in self.groups]
                + [subcommand.to_request() for subcommand in self.subcommands],
            }
            if self.name_localizations:
                model_data["name_localizations"] = _serialize_localizations(
                    self.name_localizations
                )
            if self.description_localizations:
                model_data["description_localizations"] = _serialize_localizations(
                    self.description_localizations
                )
            if self.integration_types is not None:
                model_data["integration_types"] = [
                    integration_type.value
                    for integration_type in self.integration_types
                ]
            if self.contexts is not None:
                model_data["contexts"] = [context.value for context in self.contexts]
            if self.default_member_permissions is not None:
                model_data["default_member_permissions"] = str(
                    self.default_member_permissions.value
                )
            if self.nsfw:
                model_data["nsfw"] = self.nsfw
            return command_models.RequestCommand(data=model_data)._to_request()

        return self._to_option_request()

    def _to_option_request(
        self,
    ) -> command_types._SubCommandGroupCommandOptionRequest:
        model_data: command_types.ApplicationCommandOptionRequest = {
            "type": ApplicationCommandOptionType.SUB_COMMAND_GROUP.value,
            "name": self.name,
            "description": self.description,
            "options": [group._to_option_request() for group in self.groups]
            + [subcommand.to_request() for subcommand in self.subcommands],
        }
        if self.name_localizations:
            model_data["name_localizations"] = _serialize_localizations(
                self.name_localizations
            )
        if self.description_localizations:
            model_data["description_localizations"] = _serialize_localizations(
                self.description_localizations
            )
        return command_models.Option(data=model_data)._to_request()


class PrimaryEntryPointCommandBuilder(
    _BaseApplicationCommandBuilder,
    WithDescriptionLocalizationsMixin,
    WithContextsMixin,
):
    def __init__(
        self,
        *,
        name: str,
        description: str,
        handler: ApplicationCommandHandlerType = ApplicationCommandHandlerType.APP_HANDLER,
        name_localizations: dict[Locale, str] | None = None,
        description_localizations: dict[Locale, str] | None = None,
        integration_types: list[IntegrationInstallType] | None = None,
        contexts: list[InteractionContextType] | None = None,
    ) -> None:
        super().__init__(
            type=ApplicationCommandType.PRIMARY_ENTRY_POINT,
            name=name,
            name_localizations=name_localizations,
        )
        WithDescriptionLocalizationsMixin.__init__(
            self,
            description_localizations=description_localizations,
        )
        WithContextsMixin.__init__(
            self,
            integration_types=integration_types,
            contexts=contexts,
        )

        self.description: str = description
        self.handler: ApplicationCommandHandlerType = handler

    def to_request(self) -> command_types._PrimaryEntryPointApplicationCommandRequest:
        model_data: command_types.ApplicationCommandRequest = {
            "type": self.type.value,
            "name": self.name,
            "description": self.description,
            "handler": self.handler.value,
        }

        if self.name_localizations:
            model_data["name_localizations"] = _serialize_localizations(
                self.name_localizations
            )
        if self.description_localizations:
            model_data["description_localizations"] = _serialize_localizations(
                self.description_localizations
            )
        if self.integration_types is not None:
            model_data["integration_types"] = [
                integration_type.value for integration_type in self.integration_types
            ]
        if self.contexts is not None:
            model_data["contexts"] = [context.value for context in self.contexts]

        return command_models.RequestCommand(data=model_data)._to_request()


class _BaseContextMenuCommandBuilder(_BaseApplicationCommandBuilder, WithContextsMixin):
    def __init__(
        self,
        *,
        type: ApplicationCommandType,
        name: str,
        name_localizations: dict[Locale, str] | None = None,
        integration_types: list[IntegrationInstallType] | None = None,
        contexts: list[InteractionContextType] | None = None,
    ) -> None:
        super().__init__(
            type=type,
            name=name,
            name_localizations=name_localizations,
        )
        WithContextsMixin.__init__(
            self,
            integration_types=integration_types,
            contexts=contexts,
        )


class MessageCommandBuilder(_BaseContextMenuCommandBuilder):
    def __init__(
        self,
        *,
        name: str,
        name_localizations: dict[Locale, str] | None = None,
        contexts: list[InteractionContextType] | None = None,
        integration_types: list[IntegrationInstallType] | None = None,
    ) -> None:
        super().__init__(
            type=ApplicationCommandType.MESSAGE,
            name=name,
            name_localizations=name_localizations,
            contexts=contexts,
            integration_types=integration_types,
        )

    def to_request(self) -> command_types._MessageApplicationCommandRequest:
        model_data: command_types.ApplicationCommandRequest = {
            "type": self.type.value,
            "name": self.name,
        }  # type: ignore
        if self.name_localizations:
            model_data["name_localizations"] = _serialize_localizations(
                self.name_localizations
            )
        if self.integration_types is not None:
            model_data["integration_types"] = [
                integration_type.value for integration_type in self.integration_types
            ]
        if self.contexts is not None:
            model_data["contexts"] = [context.value for context in self.contexts]
        return command_models.RequestCommand(data=model_data)._to_request()


class UserCommandBuilder(_BaseContextMenuCommandBuilder):
    def __init__(
        self,
        *,
        name: str,
        name_localizations: dict[Locale, str] | None = None,
        contexts: list[InteractionContextType] | None = None,
        integration_types: list[IntegrationInstallType] | None = None,
    ) -> None:
        super().__init__(
            type=ApplicationCommandType.USER,
            name=name,
            name_localizations=name_localizations,
            contexts=contexts,
            integration_types=integration_types,
        )

    def to_request(self) -> command_types._UserApplicationCommandRequest:
        model_data: command_types.ApplicationCommandRequest = {
            "type": self.type.value,
            "name": self.name,
        }  # type: ignore
        if self.name_localizations:
            model_data["name_localizations"] = _serialize_localizations(
                self.name_localizations
            )
        if self.integration_types is not None:
            model_data["integration_types"] = [
                integration_type.value for integration_type in self.integration_types
            ]
        if self.contexts is not None:
            model_data["contexts"] = [context.value for context in self.contexts]
        return command_models.RequestCommand(data=model_data)._to_request()
