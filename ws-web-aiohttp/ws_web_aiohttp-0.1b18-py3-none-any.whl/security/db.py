import sqlalchemy as sa


metadata = sa.MetaData()


users = sa.Table(
    'users',
    metadata,
    sa.Column('id', sa.Integer, nullable=False),
    sa.Column('userid', sa.String(256), nullable=False),
    sa.Column('disabled', sa.Boolean, nullable=False,
              server_default='FALSE'),

    # indices
    sa.PrimaryKeyConstraint('id', name='user_pkey'),
    sa.UniqueConstraint('userid', name='user_userid_key'),
)


books = sa.Table(
    'books',
    metadata,
    sa.Column('id', sa.Integer, nullable=False),
    sa.Column('user_id', sa.Integer, nullable=False),
    sa.Column('bookid', sa.String(256), nullable=False),

    # indices
    sa.PrimaryKeyConstraint('id', name='book_pkey'),
    sa.ForeignKeyConstraint(['user_id'], [users.c.id],
                            name='user_book_fkey',
                            ondelete='CASCADE'),
)
