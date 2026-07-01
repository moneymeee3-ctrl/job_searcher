"""career twin

Revision ID: b1f2c3d4e5f6
Revises: 8a59bc768e7f
Create Date: 2026-07-01 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b1f2c3d4e5f6'
down_revision: Union[str, None] = '8a59bc768e7f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'career_twins',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('last_synced_at', sa.String(length=40), nullable=True),
        sa.Column('full_name', sa.String(length=200), nullable=False),
        sa.Column('email', sa.String(length=200), nullable=False),
        sa.Column('phone', sa.String(length=50), nullable=False),
        sa.Column('location', sa.String(length=200), nullable=False),
        sa.Column('linkedin_url', sa.String(length=500), nullable=False),
        sa.Column('github_url', sa.String(length=500), nullable=False),
        sa.Column('skills', sa.JSON(), nullable=True),
        sa.Column('experience_entries', sa.JSON(), nullable=True),
        sa.Column('total_years_experience', sa.Float(), nullable=False),
        sa.Column('current_role', sa.String(length=200), nullable=False),
        sa.Column('current_company', sa.String(length=200), nullable=False),
        sa.Column('current_salary_lpa', sa.Float(), nullable=False),
        sa.Column('target_salary_lpa', sa.Float(), nullable=False),
        sa.Column('career_level', sa.String(length=30), nullable=False),
        sa.Column('career_trajectory', sa.String(length=30), nullable=False),
        sa.Column('embedded_domain_score', sa.Integer(), nullable=False),
        sa.Column('profile_completeness', sa.Integer(), nullable=False),
        sa.Column('interview_readiness_score', sa.Integer(), nullable=False),
        sa.Column('market_value_score', sa.Integer(), nullable=False),
        sa.Column('learning_velocity', sa.Float(), nullable=False),
        sa.Column('dream_companies', sa.JSON(), nullable=True),
        sa.Column('preferred_locations', sa.JSON(), nullable=True),
        sa.Column('preferred_domains', sa.JSON(), nullable=True),
        sa.Column('work_mode_preference', sa.String(length=20), nullable=False),
        sa.Column('min_salary_lpa', sa.Float(), nullable=False),
        sa.Column('open_to_relocation', sa.Boolean(), nullable=False),
        sa.Column('education_entries', sa.JSON(), nullable=True),
        sa.Column('certifications', sa.JSON(), nullable=True),
        sa.Column('projects', sa.JSON(), nullable=True),
        sa.Column('publications', sa.JSON(), nullable=True),
        sa.Column('interview_history', sa.JSON(), nullable=True),
        sa.Column('strengths', sa.JSON(), nullable=True),
        sa.Column('known_weaknesses', sa.JSON(), nullable=True),
        sa.Column('interview_style_notes', sa.String(length=1000), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('source_resume_id', sa.String(length=36), nullable=True),
        sa.Column('last_resume_parse_date', sa.String(length=40), nullable=True),
        sa.Column('change_log', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id'),
    )
    op.create_index(op.f('ix_career_twins_user_id'), 'career_twins', ['user_id'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_career_twins_user_id'), table_name='career_twins')
    op.drop_table('career_twins')
