from sqlalchemy.orm import Session
from . import models, schemas
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["pbkdf2_sha256", "argon2"], default="argon2")

def get_user(db: Session, user_id: int):
    return db.get(models.User, user_id)

def create_user(db: Session, user: schemas.UserCreate):
    """
    Creates a new user in the database.

    Args:
        db (Session): The database session to use for the operation.
        user (schemas.UserCreate): The user data to create.

    Returns:
        models.User
    """
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(name=user.name, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    return db_user

def create_payment(db: Session, payment: schemas.PaymentCreate):
    """
    Creates a new payment in the database.

    Args:
        db (Session): The database session to use for the operation.
        payment (schemas.PaymentCreate): The payment data to create.

    Returns:
        models.Payment: The newly created payment.
    """
    db_payment = models.Payment(**payment.dict())
    db.add(db_payment)
    return db_payment

def get_payment(db: Session, payment_id: int):
    return db.get(models.Payment, payment_id)

def create_transaction(db: Session, transaction: schemas.TransactionCreate):
    """
    Creates a new transaction in the database.

    Args:
        db (Session): The database session to use for the operation.
        transaction (schemas.TransactionCreate): The transaction data to create.

    Returns:
        models.Transaction: The newly created transaction.
    """
    db_transaction = models.Transaction(**transaction.dict())
    db.add(db_transaction)
    return db_transaction

def commit_session(db: Session):
    """
    Commits the database session.

    Args:
        db (Session): The database session to commit.
    """
    db.commit()