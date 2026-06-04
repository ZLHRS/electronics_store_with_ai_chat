from fastapi_limiter.depends import RateLimiter

login_limiter = RateLimiter(times=5, seconds=60)
register_limiter = RateLimiter(times=3, seconds=60)
refresh_limiter = RateLimiter(times=10, seconds=60)
