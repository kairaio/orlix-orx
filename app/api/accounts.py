from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.account import Account
from app.models.wallet import Wallet
from app.schemas.orx import AccountCreate


router = APIRouter(prefix="/api/v1/accounts", tags=["Accounts"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_account(payload: AccountCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(
        select(Account).where(Account.external_id == payload.external_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Account external_id already exists")

    account = Account(
        external_id=payload.external_id,
        display_name=payload.display_name,
        account_type=payload.account_type,
    )
    db.add(account)
    await db.flush()

    wallet = Wallet(
        account_id=account.id,
        wallet_code=f"ORX-WLT-{uuid4().hex[:16].upper()}",
        currency="ORX",
    )
    db.add(wallet)
    await db.commit()
    await db.refresh(account)
    await db.refresh(wallet)

    return {
        "account": {
            "id": account.id,
            "external_id": account.external_id,
            "display_name": account.display_name,
            "account_type": account.account_type,
            "is_active": account.is_active,
        },
        "wallet": {
            "id": wallet.id,
            "wallet_code": wallet.wallet_code,
            "currency": wallet.currency,
        },
    }


@router.get("/{account_id}")
async def get_account(account_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Account).where(Account.id == account_id))
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    wallets = await db.execute(select(Wallet).where(Wallet.account_id == account.id))
    return {
        "id": account.id,
        "external_id": account.external_id,
        "display_name": account.display_name,
        "account_type": account.account_type,
        "is_active": account.is_active,
        "wallets": [
            {
                "id": wallet.id,
                "wallet_code": wallet.wallet_code,
                "currency": wallet.currency,
                "is_active": wallet.is_active,
            }
            for wallet in wallets.scalars().all()
        ],
    }
