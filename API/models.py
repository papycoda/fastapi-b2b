from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["pbkdf2_sha256", "argon2"], default="argon2")

class User(Base):
    """
    Represents a user in the database.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    def set_password(self, password):
        """
        Sets the user's password securely.
        """
        self.hashed_password = pwd_context.hash(password)

class Payment(Base):
    """
    Represents a payment in the database.
    """

    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), index=True)
    receiver_id = Column(Integer, ForeignKey("users.id"), index=True)
    status = Column(String, default="pending", index=True)

    sender = relationship("User", foreign_keys=[sender_id], backref="sent_payments")
    receiver = relationship("User", foreign_keys=[receiver_id], backref="received_payments")

class Transaction(Base):
    """
    Represents a transaction in the database.
    """

    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(Integer, ForeignKey("payments.id"), index=True)
    status = Column(String, index=True)
    timestamp = Column(String, index=True)

    payment = relationship("Payment", backref="transactions")