from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, HTTPException

BLOCKED_IPS = {"192.168.1.10", "203.0.113.42"}

class BlockIPMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host

        if client_ip in BLOCKED_IPS:
            raise HTTPException(status_code=403, detail="Forbidden: Your IP is blocked.")

        response = await call_next(request)
        return response