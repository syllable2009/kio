from __future__ import annotations


class HealthRepository:
    """DB 层示例：真实项目里这里可以做数据库连接探活。"""

    def ping(self) -> None:
        return None

