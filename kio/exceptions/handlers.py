from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from kio.exceptions.codes import ErrorCode
from kio.exceptions.errors import AppException

logger = logging.getLogger("kio")


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def app_exception_handler(
        _request: Request, exc: AppException
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"code": exc.code, "message": exc.message},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        _request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={
                "code": ErrorCode.VALIDATION_ERROR.value,
                "message": "请求参数校验失败",
                "details": exc.errors(),
            },
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        _request: Request, exc: HTTPException
    ) -> JSONResponse:
        message, code = _normalize_http_detail(exc.detail)
        return JSONResponse(
            status_code=exc.status_code,
            content={"code": code, "message": message},
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        _request: Request, exc: Exception
    ) -> JSONResponse:
        logger.exception("未处理的异常")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "code": ErrorCode.INTERNAL_ERROR.value,
                "message": "服务器内部错误",
            },
        )


def _normalize_http_detail(detail: str | dict[str, Any]) -> tuple[str, str]:
    if isinstance(detail, dict):
        message = str(detail.get("message", detail))
        code = str(detail.get("code", ErrorCode.HTTP_ERROR.value))
        return message, code
    return str(detail), ErrorCode.HTTP_ERROR.value
