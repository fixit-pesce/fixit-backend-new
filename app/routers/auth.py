from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

from .. import utils,oauth2
from ..schemas import auth, users

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


@router.post("/change-password/{username}", status_code=status.HTTP_200_OK)
def change_password(username: str, changePassword: users.ChangePassword, db: MongoClient = Depends(get_db)):
    if username.startswith("sp-"):
        user = db["serviceProviders"].find_one({"username": username})
    
    elif username.startswith("a-"):
        user = db["admins"].find_one({"username": username})
    
    else:
        user = db["users"].find_one({"username": username})
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if not utils.verify(changePassword.current_password, user["password"]):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Incorrect password")
    
    if changePassword.new_password == changePassword.current_password:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="New password cannot be the same as current password")
    
    if username.startswith("sp-"):
        db["serviceProviders"].update_one({"username": username}, {"$set": {"password": utils.hash(changePassword.new_password)}})

    elif username.startswith("a-"):
        db["admins"].update_one({"username": username}, {"$set": {"password": utils.hash(changePassword.new_password)}})
    
    else:
        db["users"].update_one({"username": username}, {"$set": {"password": utils.hash(changePassword.new_password)}})
    
    return {"message": "Password changed"}