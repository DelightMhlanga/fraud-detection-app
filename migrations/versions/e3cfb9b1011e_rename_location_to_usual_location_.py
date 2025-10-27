"""Rename location to usual_location (nullable)

Revision ID: e3cfb9b1011e
Revises: 
Create Date: 2025-10-24 11:22:45.997265
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'e3cfb9b1011e'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # ✅ Remove leftover temp table drop
    # op.drop_table('_alembic_tmp_admin')  # ❌ Remove this line

    with op.batch_alter_table('admin', schema=None) as batch_op:
        batch_op.alter_column(
            'username',
            existing_type=sa.VARCHAR(length=100),
            type_=sa.String(length=80),
            existing_nullable=False
        )

    with op.batch_alter_table('customer', schema=None) as batch_op:
        batch_op.add_column(sa.Column('usual_location', sa.String(length=100), nullable=True))
        batch_op.drop_column('location')

    with op.batch_alter_table('transaction', schema=None) as batch_op:
        # ✅ Remove drop_constraint(None)
        # batch_op.drop_constraint(None, type_='foreignkey')  # ❌ Remove this line
        batch_op.create_foreign_key(
            'fk_transaction_customer_id',  # ✅ Provide a name
            'customer',
            ['customer_id'],
            ['id'],
            ondelete='CASCADE'
        )

def downgrade():
    with op.batch_alter_table('transaction', schema=None) as batch_op:
        batch_op.drop_constraint('fk_transaction_customer_id', type_='foreignkey')
        batch_op.create_foreign_key(
            'fk_transaction_customer_id',
            'customer',
            ['customer_id'],
            ['id']
        )

    with op.batch_alter_table('customer', schema=None) as batch_op:
        batch_op.add_column(sa.Column('location', sa.VARCHAR(length=100), nullable=False))
        batch_op.drop_column('usual_location')

    with op.batch_alter_table('admin', schema=None) as batch_op:
        batch_op.alter_column(
            'username',
            existing_type=sa.String(length=80),
            type_=sa.VARCHAR(length=100),
            existing_nullable=False
        )

    # ✅ Remove temp table recreation
    # op.create_table('_alembic_tmp_admin', ...)  # ❌ Remove this block