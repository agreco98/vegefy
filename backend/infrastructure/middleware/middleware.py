import time
from collections import defaultdict, deque
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from typing import Dict
import jwt

from config import settings



class DailyRateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.rate_limit_records: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10))
        self.max_requests = 10
        self.time_window = 60

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        path = request.url.path

        if path == "/predict":
            
            token = request.headers.get('Authorization').replace("Bearer ", "")
            payload = jwt.decode(token, settings.authentication.access_token.secret_key, settings.authentication.algorithm)
            if not payload:
                return JSONResponse(content={"detail": "Invalid or expired token"}, status_code=401)
            
            is_premium = payload.get("premium")
            
            if is_premium == False:
                current_time = time.time()
                timestamps = self.rate_limit_records[client_ip]
                
                while timestamps and current_time - timestamps[0] > self.time_window:
                    timestamps.popleft()

                if len(timestamps) >= self.max_requests:
                    return JSONResponse(content="Rate limit exceeded", status_code=429)
                
                timestamps.append(current_time)

        response = await call_next(request)
        return response