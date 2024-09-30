from fastapi import Request, Depends
from typing import Annotated, Collection, List
from motor.motor_asyncio import AsyncIOMotorGridFSBucket
from gridfs import GridFSBucket
from io import BufferedReader

from domain.users.user_model import User
from application.auth.auth import get_current_user


def get_database(request: Request) -> Collection:
    return request.app.state.db

def get_gridfs(request: Request) -> GridFSBucket:
    return request.app.state.fs

def get_models(request: Request) -> List:
    return request.app.state.detector_model, request.app.state.classification_model, request.app.state.coco_model

def get_pickle(request: Request) -> BufferedReader:
    return request.app.state.pickle_data


DatabaseDependency = Annotated[Collection, Depends(get_database)]
GridFSDependency = Annotated[GridFSBucket, Depends(get_gridfs)]
ModelsDependency = Annotated[List, Depends(get_models)]
CurrentUser = Annotated[User, Depends(get_current_user)]
PickleDependency = Annotated[BufferedReader, Depends(get_pickle)]
