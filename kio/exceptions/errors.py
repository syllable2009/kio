from __future__ import annotations

from kio.exceptions.codes import ApiCode


class AppException(Exception):
    """应用内抛出的业务异常，由全局 handler 转为统一 JSON 信封。"""

    def __init__(
        self,
        *,
        api_code: ApiCode,
        message: str,
        status_code: int,
    ) -> None:
        self.api_code = api_code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(AppException):
    def __init__(
        self,
        message: str,
        *,
        api_code: ApiCode = ApiCode.NOT_FOUND,
    ) -> None:
        super().__init__(api_code=api_code, message=message, status_code=404)


class BadRequestError(AppException):
    def __init__(
        self,
        message: str,
        *,
        api_code: ApiCode = ApiCode.BAD_REQUEST,
    ) -> None:
        super().__init__(api_code=api_code, message=message, status_code=400)


class ConflictError(AppException):
    def __init__(
        self,
        message: str,
        *,
        api_code: ApiCode = ApiCode.CONFLICT,
    ) -> None:
        super().__init__(api_code=api_code, message=message, status_code=409)


class ServerError(AppException):
    """服务端内部/依赖失败等，HTTP 500，业务码默认 50000。"""

    def __init__(
        self,
        message: str,
        *,
        api_code: ApiCode = ApiCode.SERVER_ERROR,
    ) -> None:
        super().__init__(api_code=api_code, message=message, status_code=500)
