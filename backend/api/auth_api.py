from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db import get_db
from auth import create_user_token
from economy import EconomyService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/token")
async def issue_token(user_id: str, username: str = None, db: AsyncSession = Depends(get_db)):
    """
    Выдаёт JWT для указанного user_id (MVP). Используется фронтендом автоматически.
    Также создаёт пользователя/кошелёк при необходимости.
    """
    try:
        # Гарантируем наличие кошелька/пользователя
        await EconomyService.create_user_wallet(db, user_id, username)
        token = create_user_token(user_id)
        return {"access_token": token, "token_type": "bearer", "user_id": user_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



