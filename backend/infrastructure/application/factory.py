from contextlib import asynccontextmanager
from typing import Callable, Coroutine, Iterable

from fastapi import APIRouter, FastAPI

__all__ = ("create",)


def create(
    *_,
    rest_routers: Iterable[APIRouter],
    startup_tasks: Iterable[Callable[[], Coroutine]] | None = None,
    shutdown_tasks: Iterable[Callable[[], Coroutine]] | None = None,
    **kwargs,
) -> FastAPI:

    @asynccontextmanager
    async def lifespan(app: FastAPI):

        # Define startup tasks 
        [await task() for task in startup_tasks if startup_tasks]
    
        yield
        
        # Define shutdown tasks
        [await task() for task in shutdown_tasks if shutdown_tasks]

    # Initialize the FastAPI application
    app = FastAPI(lifespan=lifespan, **kwargs)

    # Include routers
    [app.include_router(router) for router in rest_routers]
        
    return app