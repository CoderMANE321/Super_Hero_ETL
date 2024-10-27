from fastapi import FastAPI, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv("API_KEY")

app = FastAPI()

def add_heroes(hero_id):
    url = f'http://localhost:8001/heroes/'  # Base URL without query params
    params = {'hero_id': hero_id}  # Add query params

    try:
        response = requests.post(url, params=params)
        response.raise_for_status()  # Raises HTTPError for 4xx or 5xx status codes

        print(f"Hero {hero_id} added successfully:", response.json())
    except requests.exceptions.RequestException as e:
        print(f"Failed to add hero {hero_id}: {e}")