from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional
from typing import List
from datetime import datetime

from db import get_db
from services.auction import AuctionService
from services.user_profile import UserProfileService
from models import Auction, AuctionStatus
from config.settings import AUCTION_LIST_PAGE_SIZE, MARKET_ENABLED
from auth import get_current_user

router = APIRouter(prefix="/market", tags=["Market"])


class AuctionOut(BaseModel):
    id: int
    pet_id: int
    seller_user_id: str
    seller_name: str  # Анонимное имя продавца
    current_price: int
    buy_now_price: Optional[int] = None
    end_time: datetime
    status: str
    current_winner_user_id: Optional[str] = None


class AuctionDetailOut(AuctionOut):
    start_price: Optional[int] = None
    min_increment_abs: Optional[int] = None
    min_increment_pct: Optional[int] = None
    soft_close_seconds: Optional[int] = None


class AuctionListOut(BaseModel):
    items: List[AuctionOut]
    page: int
    page_size: int


class BidOut(BaseModel):
    id: int
    auction_id: int
    bidder_user_id: str
    amount: int
    created_at: datetime


class PlaceBidResponse(BaseModel):
    auction: AuctionOut
    bid: BidOut


@router.get("/auctions", response_model=AuctionListOut, response_model_exclude_none=True)
async def list_auctions(
    status: str = "active",
    page: int = 1,
    page_size: int = AUCTION_LIST_PAGE_SIZE,
    db: AsyncSession = Depends(get_db),
):
    if not MARKET_ENABLED:
        raise HTTPException(status_code=503, detail="Рынок временно недоступен")

    try:
        status_enum = AuctionStatus[status] if status in AuctionStatus.__members__ else AuctionStatus.active
        q = select(Auction).where(Auction.status == status_enum).order_by(Auction.end_time.asc())
        offset = max(0, (page - 1) * page_size)
        result = await db.execute(q.offset(offset).limit(page_size))
        auctions = result.scalars().all()
        
        # Получаем анонимные имена продавцов
        auction_items = []
        for a in auctions:
            seller_info = await UserProfileService.get_public_user_info(db, a.seller_user_id)
            seller_name = (seller_info or {}).get("public_name", "Неизвестный игрок")
            
            auction_items.append({
                "id": a.id,
                "pet_id": a.pet_id,
                "seller_user_id": a.seller_user_id,
                "seller_name": seller_name,
                "current_price": a.current_price,
                "buy_now_price": a.buy_now_price,
                "end_time": a.end_time,
                "status": a.status.value,
                "current_winner_user_id": a.current_winner_user_id,
            })
        
        return {
            "items": auction_items,
            "page": page,
            "page_size": page_size,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/auctions/{auction_id}", response_model=AuctionDetailOut, response_model_exclude_none=True)
async def get_auction(auction_id: int, db: AsyncSession = Depends(get_db)):
    if not MARKET_ENABLED:
        raise HTTPException(status_code=503, detail="Рынок временно недоступен")
    result = await db.execute(select(Auction).where(Auction.id == auction_id))
    a = result.scalar_one_or_none()
    if not a:
        raise HTTPException(status_code=404, detail="Аукцион не найден")
    
    # Получаем анонимное имя продавца
    seller_info = await UserProfileService.get_public_user_info(db, a.seller_user_id)
    seller_name = (seller_info or {}).get("public_name", "Неизвестный игрок")
    
    return {
        "id": a.id,
        "pet_id": a.pet_id,
        "seller_user_id": a.seller_user_id,
        "seller_name": seller_name,
        "start_price": a.start_price,
        "current_price": a.current_price,
        "buy_now_price": a.buy_now_price,
        "min_increment_abs": a.min_increment_abs,
        "min_increment_pct": a.min_increment_pct,
        "soft_close_seconds": a.soft_close_seconds,
        "end_time": a.end_time,
        "status": a.status.value,
        "current_winner_user_id": a.current_winner_user_id,
    }


@router.post("/auctions", response_model=dict)
async def create_auction(
    pet_id: int,
    start_price: int,
    duration_seconds: Optional[int] = None,
    buy_now_price: Optional[int] = None,
    min_increment_abs: Optional[int] = None,
    min_increment_pct: Optional[int] = None,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not MARKET_ENABLED:
        raise HTTPException(status_code=503, detail="Рынок временно недоступен")
    try:
        a = await AuctionService.create_auction(
            db=db,
            seller_user_id=current_user["user_id"],
            pet_id=pet_id,
            start_price=start_price,
            duration_seconds=duration_seconds,
            buy_now_price=buy_now_price,
            min_increment_abs=min_increment_abs,
            min_increment_pct=min_increment_pct,
        )
        return {"id": a.id, "end_time": a.end_time, "status": a.status.value}
    except (ValueError, PermissionError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/auctions/{auction_id}/bids", response_model=PlaceBidResponse, response_model_exclude_none=True)
async def place_bid(
    auction_id: int,
    amount: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not MARKET_ENABLED:
        raise HTTPException(status_code=503, detail="Рынок временно недоступен")
    try:
        a, b = await AuctionService.place_bid(db=db, auction_id=auction_id, bidder_user_id=current_user["user_id"], amount=amount)
        
        # Получаем анонимное имя продавца
        seller_info = await UserProfileService.get_public_user_info(db, a.seller_user_id)
        seller_name = (seller_info or {}).get("public_name", "Неизвестный игрок")
        
        return {
            "auction": {
                "id": a.id,
                "pet_id": a.pet_id,
                "seller_user_id": a.seller_user_id,
                "seller_name": seller_name,
                "current_price": a.current_price,
                "buy_now_price": a.buy_now_price,
                "end_time": a.end_time,
                "status": a.status.value,
                "current_winner_user_id": a.current_winner_user_id,
            },
            "bid": {
                "id": b.id,
                "auction_id": b.auction_id,
                "bidder_user_id": b.bidder_user_id,
                "amount": b.amount,
                "created_at": b.created_at,
            },
        }
    except (ValueError, PermissionError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/auctions/{auction_id}/buy_now", response_model=dict)
async def buy_now(
    auction_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not MARKET_ENABLED:
        raise HTTPException(status_code=503, detail="Рынок временно недоступен")
    try:
        a = await AuctionService.buy_now(db=db, auction_id=auction_id, buyer_user_id=current_user["user_id"])
        return {"id": a.id, "status": a.status.value}
    except (ValueError, PermissionError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/auctions/{auction_id}/cancel", response_model=dict)
async def cancel_auction(
    auction_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not MARKET_ENABLED:
        raise HTTPException(status_code=503, detail="Рынок временно недоступен")
    try:
        a = await AuctionService.cancel_auction(db=db, auction_id=auction_id, seller_user_id=current_user["user_id"])
        return {"id": a.id, "status": a.status.value}
    except (ValueError, PermissionError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


