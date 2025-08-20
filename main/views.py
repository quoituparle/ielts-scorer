from fastapi import FastAPI, status, HTTPException
import os
from google import genai
from dotenv import load_dotenv
from pydantic import BaseModel


load_dotenv()
FastAPI()

class modelSetting(BaseModel):
    model: str
    test: str
    inputText: str | None
    score: int | float | None

