from sqlalchemy.orm import Session
from . import models, schemas
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["pbkdf2_sha256", "argon2"], default="argon2")

def get_user(db: Session, user_id: int):
    return db.get(models.User, user_id)

def get_user_by_id(db: Session, user_id: int) -> models.User:
    """Fetch a user from the database by their ID."""
    return db.query(models.User).filter(models.User.id == user_id).first()

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
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
    db.commit()          # Commit the session to save the user to the database
    db.refresh(db_user)  # Refresh to get the generated id and other fields
    return db_user

def get_user_by_email(db: Session, email: str) -> models.User:
    """Fetch a user from the database by their email address."""
    return db.query(models.User).filter(models.User.email == email).first()

def create_payment(db: Session, payment: schemas.PaymentCreate) -> models.Payment:
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
    db.commit()          # Commit the session to save the payment to the database
    db.refresh(db_payment)  # Refresh to get the generated id and other fields
    return db_payment

def get_payment(db: Session, payment_id: int):
    return db.get(models.Payment, payment_id)

def create_transaction(db: Session, transaction: schemas.TransactionCreate) -> models.Transaction:
    """
    Creates a new transaction in the database.

    Args:
        db (Session): The database session to use for the operation.
        transaction (schemas.TransactionCreate): The transaction data to create.

    Returns:
        models.Transaction: The newly created transaction.
    """
    db_transaction = models.Transaction(**transaction.model_dump())
    db.add(db_transaction)
    db.commit()           # Commit the session to save the transaction to the database
    db.refresh(db_transaction)  # Refresh to get the generated id and other fields
    return db_transaction

