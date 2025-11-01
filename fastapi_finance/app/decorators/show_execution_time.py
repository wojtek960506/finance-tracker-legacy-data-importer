import time
import asyncio
from functools import wraps

def do_prints(value: float):
  message = f"Execution time - {(value / 1000): .3f} seconds"
  print('*' * len(message) * 2)
  print(message)
  print('*' * len(message) * 2)


def show_execution_time(func):

  if asyncio.iscoroutinefunction(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
      start = time.perf_counter() * 1000
      result = await func(*args, **kwargs)
      elapsed = (time.perf_counter() * 1000) - start
      do_prints(elapsed)
      return result
  else:
    @wraps(func)
    def wrapper(*args, **kwargs):
      start = time.perf_counter() * 1000
      result = func(*args, **kwargs)
      elapsed = (time.perf_counter() * 1000) - start
      do_prints(elapsed)
      return result

  return wrapper