from fastapi import Request, Depends
from typing import Annotated, Collection, List
from gridfs import GridFS

from domain.users.user_model import User
from application.auth.auth import get_current_user


def get_database(request: Request) -> Collection:
    return request.app.state.db

def get_gridfs(request: Request) -> GridFS:
    return request.app.state.fs

def get_models(request: Request) -> List:
    return request.app.state.detector_model, request.app.state.classification_model, request.app.state.coco_model


DatabaseDependency = Annotated[Collection, Depends(get_database)]
GridFSDependency = Annotated[GridFS, Depends(get_gridfs)]
ModelsDependency = Annotated[List, Depends(get_models)]
CurrentUser = Annotated[User, Depends(get_current_user)]
