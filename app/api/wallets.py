from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.wallet import Wallet
from app.services.ledger import get_wallet_balance


router = APIRouter(prefix="/api/v1/wallets", tags=["Wallets"])


@router.get("/{wallet_id}")
async def get_wallet(wallet_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Wallet).where(Wallet.id == wallet_id))
    wallet = result.scalar_one_or_none()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    balance = await get_wallet_balance(db, wallet.id)
    return {
        "id": wallet.id,
        "wallet_code": wallet.wallet_code,
        "account_id": wallet.account_id,
        "currency": wallet.currency,
        "balance": str(balance),
        "is_active": wallet.is_active,
    }


@router.get("/{wallet_id}/balance")
async def wallet_balance(wallet_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Wallet).where(Wallet.id == wallet_id))
    wallet = result.scalar_one_or_none()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    balance = await get_wallet_balance(db, wallet.id)
    return {
        "wallet_id": wallet.id,
        "wallet_code": wallet.wallet_code,
        "currency": wallet.currency,
        "balance": str(balance),
    }
