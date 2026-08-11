from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ledger import JournalEntry, LedgerEntry
from app.models.wallet import Wallet


ZERO = Decimal("0")


def normalize_amount(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.00000001"))


async def get_wallet_balance(db: AsyncSession, wallet_id: str) -> Decimal:
    result = await db.execute(
        select(func.coalesce(func.sum(LedgerEntry.amount), ZERO)).where(
            LedgerEntry.wallet_id == wallet_id
        )
    )
    return normalize_amount(Decimal(result.scalar_one()))


async def get_existing_journal(
    db: AsyncSession,
    idempotency_key: str,
) -> JournalEntry | None:
    result = await db.execute(
        select(JournalEntry).where(
            JournalEntry.idempotency_key == idempotency_key
        )
    )
    return result.scalar_one_or_none()


async def transfer(
    db: AsyncSession,
    *,
    from_wallet_id: str,
    to_wallet_id: str,
    amount: Decimal,
    idempotency_key: str,
    reference: str | None = None,
    transaction_type: str = "transfer",
) -> JournalEntry:
    amount = normalize_amount(amount)
    if amount <= ZERO:
        raise HTTPException(status_code=400, detail="Amount must be greater than zero")
    if from_wallet_id == to_wallet_id:
        raise HTTPException(status_code=400, detail="Source and destination wallets must differ")

    existing = await get_existing_journal(db, idempotency_key)
    if existing:
        return existing

    ordered_ids = sorted([from_wallet_id, to_wallet_id])
    locked = await db.execute(
        select(Wallet)
        .where(Wallet.id.in_(ordered_ids))
        .order_by(Wallet.id)
        .with_for_update()
    )
    wallets = {wallet.id: wallet for wallet in locked.scalars().all()}

    source = wallets.get(from_wallet_id)
    destination = wallets.get(to_wallet_id)
    if not source or not destination:
        raise HTTPException(status_code=404, detail="Wallet not found")
    if not source.is_active or not destination.is_active:
        raise HTTPException(status_code=409, detail="Wallet is inactive")
    if source.currency != destination.currency:
        raise HTTPException(status_code=400, detail="Wallet currencies do not match")

    balance = await get_wallet_balance(db, source.id)
    if balance < amount:
        raise HTTPException(status_code=409, detail="Insufficient ORX balance")

    journal = JournalEntry(
        transaction_id=f"ORX-TX-{uuid4().hex.upper()}",
        idempotency_key=idempotency_key,
        transaction_type=transaction_type,
        reference=reference,
        status="completed",
    )
    db.add(journal)
    await db.flush()

    db.add_all(
        [
            LedgerEntry(
                journal_id=journal.id,
                wallet_id=source.id,
                amount=-amount,
                currency=source.currency,
            ),
            LedgerEntry(
                journal_id=journal.id,
                wallet_id=destination.id,
                amount=amount,
                currency=destination.currency,
            ),
        ]
    )
    await db.commit()
    await db.refresh(journal)
    return journal


async def issue_from_treasury(
    db: AsyncSession,
    *,
    treasury_wallet_id: str,
    to_wallet_id: str,
    amount: Decimal,
    idempotency_key: str,
    reference: str | None = None,
) -> JournalEntry:
    amount = normalize_amount(amount)
    if amount <= ZERO:
        raise HTTPException(status_code=400, detail="Amount must be greater than zero")

    existing = await get_existing_journal(db, idempotency_key)
    if existing:
        return existing

    ordered_ids = sorted([treasury_wallet_id, to_wallet_id])
    locked = await db.execute(
        select(Wallet)
        .where(Wallet.id.in_(ordered_ids))
        .order_by(Wallet.id)
        .with_for_update()
    )
    wallets = {wallet.id: wallet for wallet in locked.scalars().all()}
    treasury = wallets.get(treasury_wallet_id)
    destination = wallets.get(to_wallet_id)
    if not treasury or not destination:
        raise HTTPException(status_code=404, detail="Wallet not found")
    if treasury.currency != destination.currency:
        raise HTTPException(status_code=400, detail="Wallet currencies do not match")

    journal = JournalEntry(
        transaction_id=f"ORX-TX-{uuid4().hex.upper()}",
        idempotency_key=idempotency_key,
        transaction_type="issuance",
        reference=reference,
        status="completed",
    )
    db.add(journal)
    await db.flush()
    db.add_all(
        [
            LedgerEntry(
                journal_id=journal.id,
                wallet_id=treasury.id,
                amount=-amount,
                currency=treasury.currency,
            ),
            LedgerEntry(
                journal_id=journal.id,
                wallet_id=destination.id,
                amount=amount,
                currency=destination.currency,
            ),
        ]
    )
    await db.commit()
    await db.refresh(journal)
    return journal
