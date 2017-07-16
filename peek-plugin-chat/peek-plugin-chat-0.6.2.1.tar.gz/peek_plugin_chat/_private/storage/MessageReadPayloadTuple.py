from sqlalchemy import Column, ForeignKey
from sqlalchemy import Integer, Index
from sqlalchemy.orm import relationship

from peek_plugin_base.storage.TypeDecorators import PeekLargeBinary
from peek_plugin_chat._private.PluginNames import chatTuplePrefix
from vortex.Tuple import Tuple, addTupleType
from .ChatUserTuple import ChatUserTuple
from .DeclarativeBase import DeclarativeBase
from .MessageTuple import MessageTuple


@addTupleType
class MessageReadPayloadTuple(Tuple, DeclarativeBase):
    __tupleType__ = chatTuplePrefix + 'MessageReadPayloadTuple'
    __tablename__ = 'MessageReadPayloadTuple'

    id = Column(Integer, primary_key=True, autoincrement=True)

    #: Foreign key to a Message
    messageId = Column(Integer,
                       ForeignKey(MessageTuple.id, ondelete="CASCADE"),
                       nullable=False)
    message = relationship(MessageTuple)

    #: Foreign key to a ChatUser
    ## MSSQL forces us make this nullable and use ONDELETE=NO ACTION
    chatUserId = Column(Integer,
                        ForeignKey(ChatUserTuple.id, ondelete="NO ACTION"),
                        nullable=True)
    chatUser = relationship(ChatUserTuple)

    onReadPayload = Column(PeekLargeBinary, nullable=False)

    __table_args__ = (
        Index("idx_ChatPayloads", messageId, chatUserId, unique=False),
    )
