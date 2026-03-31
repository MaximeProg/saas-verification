"""add password_hash to companies

Revision ID: 68004e4cf931
Revises: 911564d1f80e
Create Date: 2026-03-16 11:08:47.466660+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '68004e4cf931'
down_revision = '911564d1f80e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Ajouter la colonne password_hash à la table companies
    op.add_column('companies', sa.Column('password_hash', sa.String(length=255), nullable=True))
    
    # Mettre à jour les enregistrements existants avec un hash par défaut (ils devront réinitialiser leur mot de passe)
    # Note: En production, il faudrait gérer cela différemment
    op.execute("UPDATE companies SET password_hash = '' WHERE password_hash IS NULL")
    
    # Rendre la colonne non-nullable après avoir mis à jour les enregistrements existants
    op.alter_column('companies', 'password_hash', nullable=False)


def downgrade() -> None:
    # Supprimer la colonne password_hash
    op.drop_column('companies', 'password_hash')
