from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

import os
import httpx
import json

from app.database.session import get_db
from app.models.user import User


router = APIRouter()


CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")



@router.get("/github/login")
def github_login():

    github_url = (
        "https://github.com/login/oauth/authorize"
        f"?client_id={CLIENT_ID}"
        "&scope=repo user"
    )

    return RedirectResponse(github_url)



@router.get("/github/callback")
async def github_callback(
    code: str,
    db: Session = Depends(get_db)
):

    async with httpx.AsyncClient() as client:


        # Exchange code for access token
        token_response = await client.post(
            "https://github.com/login/oauth/access_token",
            headers={
                "Accept": "application/json"
            },
            data={
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "code": code
            }
        )


        token_data = token_response.json()

        access_token = token_data.get("access_token")



        # Get GitHub user
        user_response = await client.get(
            "https://api.github.com/user",
            headers={
                "Authorization": f"Bearer {access_token}"
            }
        )


        user_data = user_response.json()



        # Save user in database

        existing_user = db.query(User).filter(
            User.github_id == str(user_data["id"])
        ).first()


        if not existing_user:

            new_user = User(
                github_id=str(user_data["id"]),
                username=user_data.get("login"),
                name=user_data.get("name"),
                avatar=user_data.get("avatar_url")
            )

            db.add(new_user)
            db.commit()


        else:

            existing_user.name = user_data.get("name")
            existing_user.avatar = user_data.get("avatar_url")

            db.commit()



        # Get repositories
        repos_response = await client.get(
            "https://api.github.com/user/repos",
            headers={
                "Authorization": f"Bearer {access_token}"
            },
            params={
                "sort": "updated",
                "per_page": 10
            }
        )


        repos = repos_response.json()



    user_info = {

        "username": user_data.get("login"),

        "name": user_data.get("name"),

        "avatar": user_data.get("avatar_url"),

        "repositories": [

            {
                "name": repo["name"],
                "url": repo["html_url"],
                "language": repo["language"]
            }

            for repo in repos
        ]
    }



    return RedirectResponse(
        url=f"http://localhost:3000/dashboard?data={json.dumps(user_info)}"
    )