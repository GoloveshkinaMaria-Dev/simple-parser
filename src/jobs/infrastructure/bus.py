import json
from dataclasses import asdict

from arq.connections import ArqRedis

from src.jobs.domain.events import DomainEvent


class RedisEventBus:
    def __init__(self, redis: ArqRedis) -> None:
        self.redis = redis

    async def publish(self, event: DomainEvent) -> None:
        channel = "jobs.events"
        payload = {
            "type": type(event).__name__,
            "payload": asdict(event),
        }
        await self.redis.publish(channel, json.dumps(payload))
