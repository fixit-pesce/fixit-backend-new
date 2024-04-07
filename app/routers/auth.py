from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

from .. import utils,oauth2
from ..schemas import auth

from pymongo import MongoClient
from ..database import get_db

router = APIRouter(prefix = "/auth",tags=['Authentication'])

@router.post('/login/',response_model = auth.Token)
def login_user(user_credentials: OAuth2PasswordRequestForm = Depends(), db: MongoClient = Depends(get_db)):
    username = user_credentials.username

    if username.startswith("sp-"):
        user = db["serviceProviders"].find_one({'username': user_credentials.username})
    
    elif username.startswith("a-"):
        user = db["admins"].find_one({'username': user_credentials.username})

    else:
        user = db["users"].find_one({'username': user_credentials.username})

    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail='Invalid Credentials')
    
    if not utils.verify(user_credentials.password, user['password']):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail='Invalid Credentials')
    
    
    access_token = oauth2.create_access_token(data={'username':user['username'], 'email': user['email']})
    
    return {'access_token':access_token,'token_type':'bearer'}