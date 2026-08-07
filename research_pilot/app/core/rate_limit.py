"""
Core Rate Limiting Configuration Module using SlowAPI.

===============================================================================
EXPRESS / NODE.JS VS. FASTAPI RATE LIMITING
===============================================================================
In Node.js / Express:
  - Rate limiting is configured using `express-rate-limit` or `rate-limiter-flexible` backed by Redis:
      app.use('/api/', rateLimit({ windowMs: 15 * 60 * 1000, max: 100 }));

In FastAPI / Python (SlowAPI):
  - SlowAPI integrates with Starlette/FastAPI request pipelines.
  - `Limiter(key_func=get_remote_address)` tracks client IP addresses or user IDs.
  - Route decorators (e.g. `@limiter.limit("10/minute")`) restrict request frequencies per client.
  - Returns HTTP 429 Too Many Requests when limits are exceeded, protecting expensive LLM endpoints.
===============================================================================
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

# Global limiter instance tracking client IP addresses
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200/day", "50/hour"]
)
