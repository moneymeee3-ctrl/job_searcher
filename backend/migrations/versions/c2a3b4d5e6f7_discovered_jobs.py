"""discovered jobs

Revision ID: c2a3b4d5e6f7
Revises: b1f2c3d4e5f6
Create Date: 2026-07-01 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c2a3b4d5e6f7'
down_revision: Union[str, None] = 'b1f2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'discovered_jobs',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('external_ref', sa.String(length=300), nullable=False),
        sa.Column('dedup_key', sa.String(length=400), nullable=False),
        sa.Column('title', sa.String(length=300), nullable=False),
        sa.Column('company', sa.String(length=200), nullable=False),
        sa.Column('company_tier', sa.String(length=50), nullable=True),
        sa.Column('location', sa.String(length=200), nullable=True),
        sa.Column('source_portal', sa.String(length=100), nullable=True),
        sa.Column('source_url', sa.String(length=1000), nullable=True),
        sa.Column('apply_url', sa.String(length=1000), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('required_skills', sa.Text(), nullable=True),
        sa.Column('experience_min', sa.Integer(), nullable=True),
        sa.Column('experience_max', sa.Integer(), nullable=True),
        sa.Column('salary_min_lpa', sa.Float(), nullable=True),
        sa.Column('salary_max_lpa', sa.Float(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('last_seen_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_discovered_jobs_external_ref', 'discovered_jobs', ['external_ref'], unique=True)
    op.create_index('ix_discovered_jobs_dedup_key', 'discovered_jobs', ['dedup_key'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_discovered_jobs_dedup_key', table_name='discovered_jobs')
    op.drop_index('ix_discovered_jobs_external_ref', table_name='discovered_jobs')
    op.drop_table('discovered_jobs')
