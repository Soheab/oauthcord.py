from typing import Literal

Snowflake = int | str
Locale = Literal[
    "id",
    "da",
    "de",
    "en-GB",
    "en-US",
    "es-ES",
    "es-419",
    "fr",
    "hr",
    "it",
    "lt",
    "hu",
    "nl",
    "no",
    "pl",
    "pt-BR",
    "ro",
    "fi",
    "sv-SE",
    "vi",
    "tr",
    "cs",
    "el",
    "bg",
    "ru",
    "uk",
    "hi",
    "th",
    "zh-CN",
    "ja",
    "zh-TW",
    "ko",
]

IntegrationType = Literal[
    0,  # GUILD_INSTALL
    1,  # USER_INSTALL
]

InteractionContextType = Literal[
    0,  # GUILD
    1,  # BOT_DM
    2,  # PRIVATE_CHANNEL
]
