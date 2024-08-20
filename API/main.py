from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from . import crud, models, schemas, auth
from .database import SessionLocal, engine
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm


app = FastAPI()

# Define constants at the top of the file for better readability and maintainability
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Define the access token expiration time in minutes

@app.get("/")
def root():
    """
    Root endpoint for the FastAPI application.

    Returns:
        dict: A dictionary with a welcome message.
    """
    # Define the welcome message to be returned
    message = {"message": "Welcome to our B2B payments api"}

    # Return the welcome message
    return message

# Create all database tables using the metadata
models.Base.metadata.create_all(bind=engine)

def get_db():
    """
    Dependency function to get a database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user.

    Args:
    user (schemas.UserCreate): The user data to be created.

    Returns:
    schemas.User: The created user.
    """
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.post("/token", response_model=auth.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Login and generate an access token.

    Args:
    form_data (auth.OAuth2PasswordRequestForm): The login form data.

    Returns:
    auth.Token: The generated access token.
    """
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/payments/", response_model=schemas.Payment)
def create_payment(payment: schemas.PaymentCreate, db: Session = Depends(get_db)):
    """
    Creates a new payment in the database.

    Args:
        payment (schemas.PaymentCreate): The payment data to be created.
        db (Session): The database session to use for the operation.

    Returns:
        schemas.Payment: The newly created payment.
    """
    return crud.create_payment(db=db, payment=payment)

@app.get("/payments/{payment_id}", response_model=schemas.Payment)
def read_payment(payment_id: int, db: Session = Depends(get_db)):
    db_payment = crud.get_payment(db, payment_id=payment_id)
    if db_payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    return db_payment

@app.post("/payments/{payment_id}/transactions/", response_model=schemas.Transaction)
def create_transaction(payment_id: int, transaction: schemas.TransactionCreate, db: Session = Depends(get_db)):
    db_payment = crud.get_payment(db, payment_id=payment_id)
    if db_payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    if db_payment.status == "completed":
        raise HTTPException(status_code=400, detail="Payment already completed")

    # Simulate transaction logic (e.g., external payment processing)
    transaction.status = "completed"  # For simplicity, assume payment always succeeds
    db_payment.status = "completed"
    db.commit()
    return crud.create_transaction(db=db, transaction=transaction)
