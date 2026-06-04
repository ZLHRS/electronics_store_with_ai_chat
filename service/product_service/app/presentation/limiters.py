from fastapi_limiter.depends import RateLimiter

products_read_limiter = RateLimiter(times=120, seconds=60)
products_write_limiter = RateLimiter(times=30, seconds=60)
