"""auth_tokens

Revision ID: c6e90a4c105d
Revises: bfdc2801b5ee
Create Date: 2022-11-20 18:30:28.713415

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c6e90a4c105d'
down_revision = 'bfdc2801b5ee'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users.user_auth_token (
            user_id UUID NOT NULL PRIMARY KEY REFERENCES users.user_card(user_id),
            access_token VARCHAR(128) NOT NULL,
            access_token_expires TIMESTAMPTZ NOT NULL,
            refresh_token VARCHAR(128) NOT NULL,
            refresh_token_expires TIMESTAMPTZ NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            CONSTRAINT access_token_unique UNIQUE (access_token),
            CONSTRAINT refresh_token_unique UNIQUE (refresh_token)
        )
    """)

    conn.execute()


def downgrade():
    conn = op.get_bind()
    conn.execute(""" DROP TABLE users.user_auth_token """)
