"""ORX Genesis schema

Revision ID: 0001_orx_genesis
Revises:
Create Date: 2026-08-11
"""

from alembic import op
import sqlalchemy as sa

revision = "0001_orx_genesis"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "accounts",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("external_id", sa.String(length=120), nullable=False),
        sa.Column("display_name", sa.String(length=160), nullable=False),
        sa.Column("account_type", sa.String(length=32), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("external_id"),
    )
    op.create_index("ix_accounts_external_id", "accounts", ["external_id"], unique=True)
    op.create_index("ix_accounts_account_type", "accounts", ["account_type"], unique=False)

    op.create_table(
        "wallets",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("account_id", sa.String(length=36), nullable=False),
        sa.Column("wallet_code", sa.String(length=64), nullable=False),
        sa.Column("currency", sa.String(length=16), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("account_id", "currency", name="uq_wallet_account_currency"),
        sa.UniqueConstraint("wallet_code"),
    )
    op.create_index("ix_wallets_account_id", "wallets", ["account_id"], unique=False)
    op.create_index("ix_wallets_wallet_code", "wallets", ["wallet_code"], unique=True)

    op.create_table(
        "journal_entries",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("transaction_id", sa.String(length=64), nullable=False),
        sa.Column("idempotency_key", sa.String(length=128), nullable=False),
        sa.Column("transaction_type", sa.String(length=32), nullable=False),
        sa.Column("reference", sa.String(length=255), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("transaction_id"),
        sa.UniqueConstraint("idempotency_key"),
    )
    op.create_index("ix_journal_entries_transaction_id", "journal_entries", ["transaction_id"], unique=True)
    op.create_index("ix_journal_entries_idempotency_key", "journal_entries", ["idempotency_key"], unique=True)
    op.create_index("ix_journal_entries_transaction_type", "journal_entries", ["transaction_type"], unique=False)
    op.create_index("ix_journal_entries_status", "journal_entries", ["status"], unique=False)

    op.create_table(
        "ledger_entries",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("journal_id", sa.String(length=36), nullable=False),
        sa.Column("wallet_id", sa.String(length=36), nullable=False),
        sa.Column("amount", sa.Numeric(38, 8), nullable=False),
        sa.Column("currency", sa.String(length=16), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["journal_id"], ["journal_entries.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["wallet_id"], ["wallets.id"], ondelete="RESTRICT"),
    )
    op.create_index("ix_ledger_entries_journal_id", "ledger_entries", ["journal_id"], unique=False)
    op.create_index("ix_ledger_entries_wallet_id", "ledger_entries", ["wallet_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_ledger_entries_wallet_id", table_name="ledger_entries")
    op.drop_index("ix_ledger_entries_journal_id", table_name="ledger_entries")
    op.drop_table("ledger_entries")
    op.drop_index("ix_journal_entries_status", table_name="journal_entries")
    op.drop_index("ix_journal_entries_transaction_type", table_name="journal_entries")
    op.drop_index("ix_journal_entries_idempotency_key", table_name="journal_entries")
    op.drop_index("ix_journal_entries_transaction_id", table_name="journal_entries")
    op.drop_table("journal_entries")
    op.drop_index("ix_wallets_wallet_code", table_name="wallets")
    op.drop_index("ix_wallets_account_id", table_name="wallets")
    op.drop_table("wallets")
    op.drop_index("ix_accounts_account_type", table_name="accounts")
    op.drop_index("ix_accounts_external_id", table_name="accounts")
    op.drop_table("accounts")
