import time
from fastapi import Request, Response
from typing import Awaitable, Callable


CallNext = Callable[[Request], Awaitable[Response]]

async def add_execution_time(request: Request, call_next: CallNext):
  start = time.perf_counter()
  response = await call_next(request)
  elapsed_ms = (time.perf_counter() - start) * 1000
  response.headers["X-Execution-Time"] = f"{elapsed_ms:.2f}ms"
  return response
  