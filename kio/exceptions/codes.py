from __future__ import annotations

from enum import IntEnum


class ApiCode(IntEnum):
    """对外稳定的整数错误码 / 成功码（0 为成功）。"""

    SUCCESS = 0

    NOT_FOUND = 40401
    USER_NOT_FOUND = 40402
    MOVIE_NOT_FOUND = 40403

    BAD_REQUEST = 40001
    CONFLICT = 40901
    HTTP_ERROR = 40002

    VALIDATION_ERROR = 42201
    SERVER_ERROR = 50000
    INTERNAL_ERROR = 50001
