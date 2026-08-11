from decimal import Decimal

from pydantic import BaseModel, Field


class AccountCreate(BaseModel):
    external_id: str = Field(min_length=1, max_length=120)
    display_name: str = Field(min_length=1, max_length=160)
    account_type: str = Field(default="human", max_length=32)


class WalletCreate(BaseModel):
    account_id: str


class TransferRequest(BaseModel):
    from_wallet_id: str
    to_wallet_id: str
    amount: Decimal = Field(gt=0)
    reference: str | None = Field(default=None, max_length=255)


class TreasuryIssueRequest(BaseModel):
    to_wallet_id: str
    amount: Decimal = Field(gt=0)
    reference: str | None = Field(default=None, max_length=255)
