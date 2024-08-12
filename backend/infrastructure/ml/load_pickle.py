import pickle
from fastapi import FastAPI


async def load_pickle(app: FastAPI):
    with open("banana_characteristics.pkl", "rb") as file:
        app.state.pickle_data = pickle.load(file)