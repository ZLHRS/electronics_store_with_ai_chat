from fastapi_limiter.depends import RateLimiter

profile_read_limiter = RateLimiter(times=60, seconds=60)
profile_write_limiter = RateLimiter(times=20, seconds=60)
favorites_limiter = RateLimiter(times=30, seconds=60)
history_limiter = RateLimiter(times=60, seconds=60)
