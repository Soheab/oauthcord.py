from typing import Literal, NotRequired, TypedDict


class AccessTokenResponse(TypedDict):
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str
    scope: str  # separated by space


RefreshTokenResponse = AccessTokenResponse


class AccessTokenRequest(TypedDict):
    grant_type: Literal["authorization_code"]
    code: str
    redirect_uri: NotRequired[str]
    code_verifier: NotRequired[str]


class RefreshTokenRequest(TypedDict):
    grant_type: Literal["refresh_token"]
    refresh_token: str


class RevokeTokenRequest(TypedDict):
    token: str
    token_type_hint: NotRequired[Literal["access_token", "refresh_token"]]


class ClientCredentialsRequest(TypedDict):
    grant_type: Literal["client_credentials"]
    scope: NotRequired[str]


class ClientCredentialsResponse(TypedDict):
    access_token: str
    token_type: Literal["Bearer"]
    expires_in: int
    scope: str


class DeviceCodeRequest(TypedDict):
    scope: str


class DeviceCodeResponse(TypedDict):
    device_code: str
    user_code: str
    verification_uri: str
    verification_uri_complete: str
    expires_in: int
    interval: int


class DeviceCodeExchangeRequest(TypedDict):
    grant_type: Literal["urn:ietf:params:oauth:grant-type:device_code"]
    device_code: str


class DeviceCodeExchangePendingResponse(TypedDict):
    error: Literal[
        "authorization_pending", "slow_down", "expired_token", "access_denied"
    ]


DeviceCodeExchangeResponse = AccessTokenResponse | DeviceCodeExchangePendingResponse
