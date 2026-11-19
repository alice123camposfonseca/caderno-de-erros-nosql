"""Operações Redis usadas pela autenticação e pelas métricas probabilísticas."""

import json
from datetime import date

from redis import Redis
from redis.exceptions import ResponseError


class RedisService:
    def __init__(self, url: str):
        self.client = Redis.from_url(url, decode_responses=True)

    def ping(self) -> None:
        self.client.ping()

    def prepare_structures(self) -> None:
        """Cria o Count-Min Sketch uma única vez.

        O Bloom Filter é criado automaticamente pelo primeiro BF.ADD e o
        HyperLogLog pelo primeiro PFADD.
        """
        for key in ("stats:login-frequency", "stats:event-frequency"):
            try:
                self.client.execute_command("CMS.INITBYDIM", key, 2000, 5)
            except ResponseError as error:
                if "exists" not in str(error).lower():
                    raise

    def email_is_known(self, email: str) -> bool:
        return bool(self.client.execute_command("BF.EXISTS", "users:emails", email))

    def remember_email(self, email: str) -> None:
        self.client.execute_command("BF.ADD", "users:emails", email)

    def get_cached_user(self, email: str) -> dict | None:
        value = self.client.get(f"auth:user:{email}")
        return json.loads(value) if value else None

    def cache_user(self, user: dict) -> None:
        self.client.setex(f"auth:user:{user['email']}", 900, json.dumps(user))

    def create_session(self, token: str, user: dict, ttl_seconds: int) -> None:
        session = {"id": str(user["_id"]), "nome": user["nome"], "email": user["email"]}
        self.client.setex(f"auth:session:{token}", ttl_seconds, json.dumps(session))

    def get_session(self, token: str) -> dict | None:
        key = f"auth:session:{token}"
        value = self.client.get(key)
        if value:
            self.client.expire(key, 1800)
            return json.loads(value)
        return None

    def delete_session(self, token: str) -> None:
        self.client.delete(f"auth:session:{token}")

    def track_login(self, user_id: str) -> None:
        daily_key = f"stats:unique-users:{date.today().isoformat()}"
        self.client.pfadd(daily_key, user_id)
        self.client.execute_command("CMS.INCRBY", "stats:login-frequency", user_id, 1)

    def unique_users_today(self) -> int:
        return self.client.pfcount(f"stats:unique-users:{date.today().isoformat()}")

    def login_frequency(self, user_id: str) -> int:
        return int(
            self.client.execute_command("CMS.QUERY", "stats:login-frequency", user_id)[0]
        )

    def track_event(self, event_name: str) -> None:
        self.client.execute_command("CMS.INCRBY", "stats:event-frequency", event_name, 1)

    def event_frequency(self, event_name: str) -> int:
        return int(
            self.client.execute_command("CMS.QUERY", "stats:event-frequency", event_name)[0]
        )

    def close(self) -> None:
        self.client.close()
