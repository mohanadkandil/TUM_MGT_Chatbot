import logging
import os

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware

# Logger configuration
logger = logging.getLogger("proxy_logger")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter(...)
handler.setFormatter(formatter)
logger.addHandler(handler)

app = FastAPI()

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ProxyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        ...


# Add the modified middleware
app.add_middleware(ProxyMiddleware)

# Serve static files
app.mount("", StaticFiles(directory="dist/uploadservice", html=True), name="static")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 3000))
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=port)
