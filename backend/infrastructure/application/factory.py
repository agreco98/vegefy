from contextlib import asynccontextmanager
from typing import Callable, Coroutine, Iterable, List, Type
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.middleware.cors import CORSMiddleware

from fastapi import APIRouter, FastAPI

__all__ = ("create",)


def create(
    *_,
    rest_routers: Iterable[APIRouter],
    startup_tasks: Iterable[Callable[[], Coroutine]] | None = None,
    shutdown_tasks: Iterable[Callable[[], Coroutine]] | None = None,
    middlewares: List[Type[BaseHTTPMiddleware]] = None,
    **kwargs,
) -> FastAPI:

    @asynccontextmanager
    async def lifespan(app: FastAPI):

        # Define startup tasks 
        [await task(app) for task in startup_tasks if startup_tasks]
    
        yield
        
        # Define shutdown tasks
        [await task(app) for task in shutdown_tasks if shutdown_tasks]

    # Initialize the FastAPI application
    app = FastAPI(lifespan=lifespan, **kwargs)

    # Include routers
    [app.include_router(router) for router in rest_routers]

    app.add_middleware(
        CORSMiddleware, 
        allow_origins=["*"], 
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
        )

    # Add middlewares
    if middlewares:
        [app.add_middleware(middleware) for middleware in middlewares]

    return app