
from typing import Annotated, List, Optional
import uuid
from fastapi import FastAPI,HTTPException, Response
from dotenv import dotenv_values
import motor.motor_asyncio
from pydantic import BaseModel, BeforeValidator, Field, TypeAdapter
from bson import ObjectId
from pymongo import ReturnDocument
config = dotenv_values(".env")

client = motor.motor_asyncio.AsyncIOMotorClient(config["MONGO_URL"])
db = client.tank_man

app = FastAPI()

PyObjectId = Annotated[str, BeforeValidator(str)]


class Tank(BaseModel):
    id:Optional[PyObjectId] = Field(alias="_id", default=None) 
    location: Optional[str] = None
    lat: Optional[float] = None
    long: Optional[float] = None

@app.get("/tank")
async def get_tank():
    tanks = await db["tanks"].find().to_list(999)
    return TypeAdapter(List[Tank]).validate_python(tanks)

@app.get("/tank/{id}")
async def get_tanks(id:str):
    tank = await db["tanks"].find_one({"_id": ObjectId(id)})
    return Tank(**tank)

@app.post("/tank", status_code=201)
async def created_tank(tank: Tank):
    new_tank = await db["tanks"].insert_one(tank.model_dump())

    created_tank = await db["tanks"].find_one({"_id":new_tank.inserted_id})
    return Tank(**created_tank)

@app.patch("/tank/{id}")
async def update_tank(id:str, tank_update: Tank):
    updated_tank = await db["tank"].update_one({"_id": ObjectId(id)}, {"$set": tank_update})

    if updated_tank.modified_count > 0:
        patched_tank = await db["tanks"].find_one({"_id" : ObjectId(id)})
        print(patched_tank)
        return patched_tank
    raise HTTPException(status_code=404,detail="Tank of id:" + id + "not found.")
    

@app.delete("tank/{id}",status_code=204)
async def delete_tank(id : str):
    deleted_tank  = await db["tanks"].delete_one({"_id" : ObjectId(id)})
   
    if deleted_tank.deleted_count < 1:

        raise HTTPException(status_code=404,detail="Tank of id" + id + "not found.")
    

  
    
class Profile(BaseModel):
    id:Optional[PyObjectId] = Field(alias="_id", default=None) 
    username: Optional[str] = None
    role: Optional[str] = None
    color: Optional[str] = None
    time : Optional[str] = None


@app.get("/profile")
async def get_profile():
    profiles = await db["profiles"].find().to_list(999)
    return TypeAdapter(List[Profile]).validate_python(profiles)

@app.post("/profile", status_code=201)
async def created_profile(profile: Profile):
    new_profile = await db["profiles"].insert_one(profile.model_dump())

    created_profile = await db["profiles"].find_one({"_id":new_profile.inserted_id})
    return Profile(**created_profile)
