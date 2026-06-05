from fastapi_limiter.depends import RateLimiter

orders_limiter = RateLimiter(times=30, seconds=60)
