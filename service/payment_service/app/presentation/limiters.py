from fastapi_limiter.depends import RateLimiter

payment_limiter = RateLimiter(times=30, seconds=60)
