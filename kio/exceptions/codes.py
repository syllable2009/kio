from __future__ import annotations

from enum import StrEnum


class ErrorCode(StrEnum):
    """对外稳定的业务/协议错误码（与 HTTP 状态码分离，便于客户端分支）。"""

    # 通用
    NOT_FOUND = "NOT_FOUND"
    BAD_REQUEST = "BAD_REQUEST"
    CONFLICT = "CONFLICT"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    HTTP_ERROR = "HTTP_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"

    # 领域
    USER_NOT_FOUND = "USER_NOT_FOUND"
    MOVIE_NOT_FOUND = "MOVIE_NOT_FOUND"
