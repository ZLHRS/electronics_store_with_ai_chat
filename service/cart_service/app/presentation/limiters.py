from fastapi_limiter.depends import RateLimiter

cart_limiter = RateLimiter(times=60, seconds=60)
