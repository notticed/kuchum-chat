from fastapi import FastAPI, Depends, Request, Response, Cookie, APIRouter
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi_jwt_auth.exceptions import (
    InvalidHeaderError,
    CSRFError,
    JWTDecodeError,
    RevokedTokenError,
    MissingTokenError,
    AccessTokenRequired,
    RefreshTokenRequired,
    FreshTokenRequired
)
from pydantic import BaseModel
from connection import *
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from hashing import *
from bson.objectid import ObjectId
from typing import Optional
import base64
import json
import jwt
from typing import Callable, List
from fastapi.routing import APIRoute


origins = [
  "https://kuch-chat.vercel.app"
]

middleware = [
  Middleware(CORSMiddleware, allow_origins=origins)
]

app = FastAPI(middleware=middleware)


# Handle CORS
class CORSHandler(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def preflight_handler(request: Request) -> Response:
            if request.method == 'OPTIONS':
                response = Response()
                response.headers['Access-Control-Allow-Origin'] = '*'
                response.headers['Access-Control-Allow-Methods'] = 'POST, GET, DELETE, OPTIONS'
                response.headers['Access-Control-Allow-Headers'] = 'Authorization, Content-Type'
            else:
                response = await original_route_handler(request)

        return preflight_handler

router = APIRouter(route_class=CORSHandler)
app.include_router(router)

class CRUD:
  def __init__(self, collection):
    self.collection = collection
    
  def create(self, scheme): 
    try:
      self.collection.insert_one(scheme)
      return True
    except:
      return False

  def delete(self, id):
    try:
      self.collection.delete_one({'_id': ObjectId(id)})
      return True
    except:
      return False

  def update(self, id, value):
    try:
      self.collection.update_one({'_id': ObjectId(id)}, {"$set": value}, upsert=False)
      return True
    except:
      return False
    
  def get_all(self):
    try:
      all = []
      for item in self.collection.find():
        item['_id'] = str(item['_id'])
        all.append(item)
      return all
    except:
      return None
    
  def get_id(self, id):
    try: 
      result_id = self.collection.find_one({'_id': ObjectId(id)})
      result_id['_id'] = str(result_id['_id'])
      return result_id
    except: 
      return {'msg': 'Not found'}
    

class User(BaseModel):
  nick: str
  password: str

class Message(BaseModel):
  message: str

def user_payload(nick, password):
  user_payload = {
    'nick': nick,
    'password': hashing(password)
  }
  return user_payload


def chat_scheme(nick, id1, nick2, id2):
  chat_scheme = {
    'relate': [
      [nick, id1],
      [nick2, id2]
    ],
    'history': []
  }
  return chat_scheme


def message_scheme(user_id, nick, message):
  message_scheme = {
    'user': [user_id, nick],
    'message': message
  }
  return message_scheme

# AuthJWT class settings
class Settings(BaseModel):
  authjwt_secret_key: str = "secret"
  authjwt_token_location: set = {"cookies"}
  authjwt_cookie_csrf_protect: bool = False

@AuthJWT.load_config
def get_config():
    return Settings()

# error handler
@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )
