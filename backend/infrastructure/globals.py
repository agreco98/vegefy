from fastapi import Request, Depends
from typing import Annotated, Collection


def get_database(request: Request) -> Collection:
    return request.app.state.db

DatabaseDependency = Annotated[Collection, Depends(get_database)]