from typing import List
from fastapi import FastAPI, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from . import crud, models, schemas, auth
from .database import SessionLocal, engine
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from xhtml2pdf import pisa
from fastapi.responses import FileResponse
#from .schemas import Receipt
from io import BytesIO
from fastapi.responses import FileResponse
from .crud import get_payment, get_user_by_id

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


@app.get("/users/{user_id}/transactions/", response_model=List[schemas.Transaction])
def get_user_transactions(user_id: int, db: Session = Depends(get_db)):
    user = crud.get_user(db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return db.query(models.Transaction).join(models.Payment).filter(
        (models.Payment.sender_id == user_id) | (models.Payment.receiver_id == user_id)
    ).all()


# def generate_pdf_with_xhtml2pdf(receipt: Receipt) -> BytesIO:
#     html_content = f"""
#     <html>
#     <head><title>Receipt</title></head>
#     <body>
#         <h1>Receipt for Payment ID: {receipt.payment_id}</h1>
#         <p>Amount: ${receipt.amount}</p>
#         <p>Sender: {receipt.sender}</p>
#         <p>Receiver: {receipt.receiver}</p>
#         <p>Status: {receipt.status}</p>
#         <p>Timestamp: {receipt.timestamp}</p>
#     </body>
#     </html>
#     """
#     pdf_file = BytesIO()
#     pisa.CreatePDF(BytesIO(html_content.encode('utf-8')), dest=pdf_file)
#     pdf_file.seek(0)
#     return pdf_file


# @app.get("/payments/{payment_id}/receipt")
# def generate_receipt(
#     payment_id: int,
#     format: str = Query("pdf", enum=["pdf", "image"]),
#     db: Session = Depends(get_db)
# ):
#     # Retrieve the payment
#     db_payment = get_payment(db, payment_id)
#     if db_payment is None:
#         raise HTTPException(status_code=404, detail="Payment not found")

#     # Check if the payment is completed
#     if db_payment.status != "completed":
#         raise HTTPException(status_code=400, detail="Receipt can only be generated for completed payments")

#     # Retrieve sender and receiver details
#     sender = get_user_by_id(db, db_payment.sender_id)
#     receiver = get_user_by_id(db, db_payment.receiver_id)

#     # Create the receipt object
#     receipt = Receipt(
#         payment_id=db_payment.id,
#         amount=db_payment.amount,
#         sender=sender.name,
#         receiver=receiver.name,
#         status=db_payment.status,
#         timestamp=db_payment.transactions[-1].timestamp  
#     )

#     # Generate the appropriate file based on user's choice
#     if format == "pdf":
#         pdf_file = generate_pdf_with_xhtml2pdf(receipt)  
#         return FileResponse(pdf_file, media_type="application/pdf", filename="receipt.pdf")
#     elif format == "image":
#         image_file = generate_image(receipt) 
#         return FileResponse(image_file, media_type="image/png", filename="receipt.png")
