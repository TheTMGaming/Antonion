from app.internal.exceptions.ErrorResponse import ErrorResponse


class UnauthorizedException(Exception):
    pass


class UnauthorizedResponse(ErrorResponse):
    @staticmethod
    def message() -> str:
        return "Unauthorized"

    @staticmethod
    def status() -> int:
        return 401


class UndefinedRefreshTokenException(Exception):
    pass


class UndefinedRefreshTokenResponse(ErrorResponse):
    @staticmethod
    def message() -> str:
        return "Refresh token is undefined"

    @staticmethod
    def status() -> int:
        return 400


class InvalidPayloadException(Exception):
    pass


class InvalidPayloadResponse(ErrorResponse):
    @staticmethod
    def message() -> str:
        return "Access token's payload is invalid"

    @staticmethod
    def status() -> int:
        return 400


class AccessTokenTTLZeroException(Exception):
    pass


class AccessTokenTTLZeroResponse(ErrorResponse):
    @staticmethod
    def message() -> str:
        return "TTL is zero"

    @staticmethod
    def status() -> int:
        return 400


class UnknownRefreshTokenException(Exception):
    pass


class UnknownRefreshTokenResponse(ErrorResponse):
    @staticmethod
    def message() -> str:
        return "Unknown refresh token"

    @staticmethod
    def status() -> int:
        return 400


class RevokedRefreshTokenException(Exception):
    pass


class RevokedRefreshTokenResponse(ErrorResponse):
    @staticmethod
    def message() -> str:
        return "Refresh token was be revoked"

    @staticmethod
    def status() -> int:
        return 400
