"""users

Revision ID: bfdc2801b5ee
Revises: 
Create Date: 2022-11-20 17:50:28.095045

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bfdc2801b5ee'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    conn.execute('CREATE SCHEMA IF NOT EXISTS "users"')

    conn.execute(""" CREATE TYPE users.user_role AS ENUM (
            'USER',
            'MODERATOR',
            'ADMIN',
            'OWNER'
        ) """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users.user_card (
            user_id UUID NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
            roles users.user_role[] NOT NULL DEFAULT '{USER}',

            user_name VARCHAR(32) NULL,
            
            email VARCHAR(64) NULL,
            
            photo UUID NULL,

            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """)


def downgrade():
    conn = op.get_bind()
    conn.execute(""" DROP TABLE users.user_card """)
    conn.execute(""" DROP TYPE users.user_role """)
    conn.execute(""" DROP SCHEMA users """)
