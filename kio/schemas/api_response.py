from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ApiResponse(BaseModel):
    """统一 API 响应：code + message + data 信封。

    约定：
    - code == 0 表示成功，message 为空字符串
    - code != 0 表示失败，message 为错误信息
    - data 为任意类型载荷：业务对象、列表、字符串、boolean 等
    """

    code: int = Field(description="0 表示成功，非 0 为错误码（与 HTTP 状态可独立映射）")
    message: str = Field(default="", description="code!=0 时的错误信息；成功时为空字符串")
    data: Any = Field(
        default=None, description="成功时为业务数据；失败时为错误细节（可为 None）"
    )
