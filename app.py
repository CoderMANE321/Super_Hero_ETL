from fastapi import FastAPI, HTTPException
from sqlmodel import Field, Session, SQLModel, create_engine, select
from config import settings
from utils.getHeroes import add_heroes
import requests
from typing import Optional
from utils.getHeroes import add_heroes

class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    first_appearance: Optional[str] = Field(default='not found', index=True)
    aliases: Optional[str] = Field(default='not found', index=True)
    base: Optional[str] = Field(default='not found', index=True)


engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))



def drop_and_recreate_tables():
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)


app = FastAPI()


@app.on_event("startup")
def on_startup():
    drop_and_recreate_tables()




@app.post("/heroes/")
def create_hero(hero_id: int):
    # Construct the URL for the superhero API
    url = f'https://superheroapi.com/api/apiKey/{hero_id}'
    
    try:
        # Fetch data from superhero API
        response = requests.get(url)
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to fetch hero data")
        
        hero_data = response.json()
        
        # Extract only the fields we want
        hero = Hero(
            id=hero_id,
            name=hero_data["name"],
            first_appearance=hero_data["biography"]["first-appearance"],
            aliases=", ".join(hero_data["biography"]["aliases"]),  # Convert list to string
            base=hero_data["work"]["base"]
        )
        
        # Save to database
        with Session(engine) as session:
            session.add(hero)
            session.commit()
            session.refresh(hero)
            
            return {
                "message": "Hero saved successfully!",
                "hero": hero
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_heroes():
    with Session(engine) as session:
        heroes = session.exec(select(Hero)).all()
        return heroes


@app.get("/heroes/{hero_id}", response_model=Hero)
def read_hero(hero_id: int):
    with Session(engine) as session:
        hero = session.get(Hero, hero_id)
        if not hero:
            raise HTTPException(status_code=404, detail="Hero not found")
        return hero
    

