import redis.asyncio as redis
from src.config import settings

redis_client = redis.from_url(
    settings.REDIS_URL,
    decode_responses=True
)

JTI_EXPIRY = 3600


async def add_jti_to_blocklist(jti: str):
    await redis_client.set(jti, "revoked", ex=JTI_EXPIRY)


async def token_in_blocklist(jti: str) -> bool:
    token = await redis_client.get(jti)
    return token is not None