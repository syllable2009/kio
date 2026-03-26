from __future__ import annotations


class UserRepository:
    """用户数据访问层（Mock 数据）。"""

    _MOCK_USERS = [
        {"id": 1, "name": "张三", "email": "zhangsan@example.com"},
        {"id": 2, "name": "李四", "email": "lisi@example.com"},
        {"id": 3, "name": "王五", "email": "wangwu@example.com"},
    ]

    def get_all(self) -> list[dict]:
        return self._MOCK_USERS

    def get_by_id(self, user_id: int) -> dict | None:
        for user in self._MOCK_USERS:
            if user["id"] == user_id:
                return user
        return None
