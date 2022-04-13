from sqlalchemy import Column, Integer, BigInteger, String, ForeignKey, DateTime, func
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class UserOrm(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, index=True, nullable=False)
    webapp_id = Column(BigInteger, index=True, nullable=True)

    created_at = Column(DateTime, server_default=func.now())
    activated_at = Column(DateTime, default=None)

    token = Column(String(36), index=True)
    token_expires_at = Column(DateTime)

    chats = relationship("ChatOrm", back_populates="user", cascade="all, delete-orphan")

    __mapper_args__ = {"eager_defaults": True}

    @property
    def is_active(self) -> bool:
        return self.activated_at is not None

    def __repr__(self) -> str:
        return f"UserOrm(id={self.id!r}, telegram_id={self.telegram_id!r})"


class ChatOrm(Base):
    __tablename__ = "chat"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, index=True, nullable=False)

    type = Column(String(30), nullable=False)

    user_id = Column(Integer, ForeignKey("user.id"), nullable=True)

    user = relationship("UserOrm", back_populates="chats")

    def __repr__(self) -> str:
        return f"ChatOrm(id={self.id!r}, telegram_id={self.telegram_id!r})"
