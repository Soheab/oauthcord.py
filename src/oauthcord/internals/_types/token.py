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
    redirect_uri: str


class RefreshTokenRequest(TypedDict):
    grant_type: Literal["refresh_token"]
    refresh_token: str


class RevokeTokenRequest(TypedDict):
    token: str
    token_type_hint: NotRequired[Literal["access_token", "refresh_token"]]
