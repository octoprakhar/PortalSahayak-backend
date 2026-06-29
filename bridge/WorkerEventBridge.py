import asyncio
from asyncio import AbstractEventLoop,Future
from typing import Any
from collections.abc import Coroutine

class WorkerEventBridge:
    """
    This bridge will help schedule coroutines from worker thread to the main thread
    """
    def __init__(self, event_loop: AbstractEventLoop):
        self.event_loop = event_loop

    def dispatch(self,coroutine:Coroutine[Any,Any,Any]):
        futures = asyncio.run_coroutine_threadsafe(coro=coroutine,loop=self.event_loop)
        return futures