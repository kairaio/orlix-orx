from uuid import uuid4

from fastapi import APIRouter, Depends, Header
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.security import require_admin_key
from app.models.account import Account
from app.models.wallet import Wallet
from app.schemas.orx import TreasuryIssueRequest
from app.services.ledger import issue_from_treasury


router = APIRouter(prefix="/api/v1/treasury", tags=["Treasury"])


async def get_or_create_treasury_wallet(db: AsyncSession) -> Wallet:
    account_result = await db.execute(
        select(Account).where(Account.external_id == settings.treasury_external_id)
    )
    account = account_result.scalar_one_or_none()
    if not account:
        account = Account(
            external_id=settings.treasury_external_id,
            display_name="ORX Treasury",
            account_type="system",
        )
        db.add(account)
        await db.flush()

    wallet_result = await db.execute(
        select(Wallet).where(
            Wallet.account_id == account.id,
            Wallet.currency == settings.currency_code,
        )
    )
    wallet = wallet_result.scalar_one_or_none()
    if not wallet:
        wallet = Wallet(
            account_id=account.id,
            wallet_code=f"ORX-TREASURY-{uuid4().hex[:12].upper()}",
            currency=settings.currency_code,
        )
        db.add(wallet)
        await db.flush()

    return wallet


@router.post("/issue", dependencies=[Depends(require_admin_key)])
async def issue_orx(
    payload: TreasuryIssueRequest,
    db: AsyncSession = Depends(get_db),
    x_idempotency_key: str = Header(...),
):
    treasury_wallet = await get_or_create_treasury_wallet(db)
    journal = await issue_from_treasury(
        db,
        treasury_wallet_id=treasury_wallet.id,
        to_wallet_id=payload.to_wallet_id,
        amount=payload.amount,
        idempotency_key=x_idempotency_key,
        reference=payload.reference,
    )
    return {
        "transaction_id": journal.transaction_id,
        "type": journal.transaction_type,
        "status": journal.status,
        "reference": journal.reference,
        "created_at": journal.created_at,
    }
