from __future__ import annotations

from kio.exceptions.codes import ErrorCode


class AppException(Exception):
    """应用内抛出的业务异常，由全局 handler 转为统一 JSON。"""

    def __init__(
        self,
        *,
        code: str,
        message: str,
        status_code: int,
    ) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(AppException):
    def __init__(
        self,
        message: str,
        *,
        code: ErrorCode = ErrorCode.NOT_FOUND,
    ) -> None:
        super().__init__(code=code.value, message=message, status_code=404)


class BadRequestError(AppException):
    def __init__(
        self,
        message: str,
        *,
        code: ErrorCode = ErrorCode.BAD_REQUEST,
    ) -> None:
        super().__init__(code=code.value, message=message, status_code=400)


class ConflictError(AppException):
    def __init__(
        self,
        message: str,
        *,
        code: ErrorCode = ErrorCode.CONFLICT,
    ) -> None:
        super().__init__(code=code.value, message=message, status_code=409)
