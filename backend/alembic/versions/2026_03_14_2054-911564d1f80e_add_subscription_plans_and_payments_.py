"""add subscription plans and payments tables

Revision ID: 911564d1f80e
Revises: 
Create Date: 2026-03-14 20:54:10.296145+00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '911564d1f80e'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Créer la table subscription_plans
    op.create_table(
        'subscription_plans',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('slug', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=True),
        sa.Column('billing_period', sa.String(length=20), nullable=True),
        sa.Column('monthly_quota', sa.Integer(), nullable=False),
        sa.Column('max_api_keys', sa.Integer(), nullable=True),
        sa.Column('max_users', sa.Integer(), nullable=True),
        sa.Column('features', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('advantages', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_popular', sa.Boolean(), nullable=True),
        sa.Column('is_custom', sa.Boolean(), nullable=True),
        sa.Column('display_order', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('slug')
    )
    
    # Créer la table payments
    op.create_table(
        'payments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('payment_reference', sa.String(length=100), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('plan_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=True),
        sa.Column('fedapay_transaction_id', sa.String(length=255), nullable=True),
        sa.Column('fedapay_token', sa.String(length=255), nullable=True),
        sa.Column('fedapay_status', sa.String(length=50), nullable=True),
        sa.Column('fedapay_response', sa.Text(), nullable=True),
        sa.Column('payment_method', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('paid_at', sa.DateTime(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('customer_email', sa.String(length=255), nullable=True),
        sa.Column('customer_phone', sa.String(length=20), nullable=True),
        sa.Column('callback_url', sa.String(length=500), nullable=True),
        sa.Column('return_url', sa.String(length=500), nullable=True),
        sa.Column('metadata', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.ForeignKeyConstraint(['plan_id'], ['subscription_plans.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('payment_reference'),
        sa.UniqueConstraint('fedapay_transaction_id')
    )
    
    # Ajouter les colonnes à la table companies
    op.add_column('companies', sa.Column('subscription_plan_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('companies', sa.Column('subscription_started_at', sa.DateTime(), nullable=True))
    
    # Créer les index
    op.create_index(op.f('ix_payments_company_id'), 'payments', ['company_id'], unique=False)
    op.create_index(op.f('ix_payments_status'), 'payments', ['status'], unique=False)


def downgrade() -> None:
    # Supprimer les index
    op.drop_index(op.f('ix_payments_status'), table_name='payments')
    op.drop_index(op.f('ix_payments_company_id'), table_name='payments')
    
    # Supprimer les colonnes de companies
    op.drop_column('companies', 'subscription_started_at')
    op.drop_column('companies', 'subscription_plan_id')
    
    # Supprimer les tables
    op.drop_table('payments')
    op.drop_table('subscription_plans')
