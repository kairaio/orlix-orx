from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.ledger import JournalEntry, LedgerEntry
from app.schemas.orx import TransferRequest
from app.services.ledger import transfer


router = APIRouter(prefix="/api/v1/transactions", tags=["Transactions"])


@router.post("/transfer")
async def transfer_orx(
    payload: TransferRequest,
    db: AsyncSession = Depends(get_db),
    x_idempotency_key: str = Header(...),
):
    journal = await transfer(
        db,
        from_wallet_id=payload.from_wallet_id,
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


@router.get("/{transaction_id}")
async def get_transaction(transaction_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(JournalEntry).where(JournalEntry.transaction_id == transaction_id)
    )
    journal = result.scalar_one_or_none()
    if not journal:
        raise HTTPException(status_code=404, detail="Transaction not found")

    entries_result = await db.execute(
        select(LedgerEntry).where(LedgerEntry.journal_id == journal.id)
    )
    entries = entries_result.scalars().all()
    return {
        "transaction_id": journal.transaction_id,
        "type": journal.transaction_type,
        "status": journal.status,
        "reference": journal.reference,
        "created_at": journal.created_at,
        "entries": [
            {
                "wallet_id": entry.wallet_id,
                "amount": str(entry.amount),
                "currency": entry.currency,
            }
            for entry in entries
        ],
    }
