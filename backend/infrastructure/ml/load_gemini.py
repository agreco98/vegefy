import google.generativeai as genai
from fastapi import FastAPI

from config import settings

def load_gemini(app: FastAPI):
    genai.configure(api_key=settings.gemini.api_key)
    