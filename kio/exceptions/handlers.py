from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from kio.exceptions.codes import ApiCode
from kio.exceptions.errors import AppException

logger = logging.getLogger("kio")


def _envelope(api_code: int, message: str, data: Any) -> dict[str, Any]:
    return {"code": api_code, "message": message, "data": data}


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def app_exception_handler(
        _request: Request, exc: AppException
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=_envelope(int(exc.api_code), exc.message, None),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        _request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content=_envelope(
                ApiCode.VALIDATION_ERROR.value,
                "请求参数校验失败",
                {"details": exc.errors()},
            ),
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        _request: Request, exc: HTTPException
    ) -> JSONResponse:
        message, api_code = _normalize_http_detail(exc.detail)
        return JSONResponse(
            status_code=exc.status_code,
            content=_envelope(api_code, message, None),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        _request: Request, exc: Exception
    ) -> JSONResponse:
        logger.exception("未处理的异常")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_envelope(
                ApiCode.INTERNAL_ERROR.value,
                "服务器内部错误",
                None,
            ),
        )


def _normalize_http_detail(detail: str | dict[str, Any]) -> tuple[str, int]:
    if isinstance(detail, dict):
        message = str(detail.get("message", detail))
        raw = detail.get("code", ApiCode.HTTP_ERROR.value)
        api_code = int(raw) if isinstance(raw, int) else ApiCode.HTTP_ERROR.value
        return message, api_code
    return str(detail), ApiCode.HTTP_ERROR.value
