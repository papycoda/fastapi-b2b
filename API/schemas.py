from pydantic import BaseModel, Field
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], default="pbkdf2_sha256")

class ConfiguredBaseModel(BaseModel):
    class Config:
        from_attributes = True

class UserBase(ConfiguredBaseModel):
    name: str
    email: str

class UserCreate(UserBase):
    password: str

    def __init__(self, **data):
        super().__init__(**data)
        self.password = pwd_context.hash(self.password)

class User(UserBase):
    id: int

class PaymentBase(ConfiguredBaseModel):
    amount: float
    sender_id: int
    receiver_id: int

class PaymentCreate(PaymentBase):
    pass

class Payment(PaymentBase):
    id: int
    status: str

class TransactionBase(ConfiguredBaseModel):
    status: str

class TransactionCreate(TransactionBase):
    pass

class Transaction(TransactionBase):
    id: int
    payment_id: int
    timestamp: str

# class Receipt(BaseModel):
#     payment_id: int
#     amount: float
#     sender: str
#     receiver: str
#     status: str
#     timestamp: str

# Example usage:
# user_create = UserCreate(name="John Doe", email="johndoe@example.com", password="mysecretpassword")
# print(user_create.password)  # Output: hashed password

# payment_create = PaymentCreate(amount=10.99, sender_id=1, receiver_id=2)
# print(payment_create)  # Output: PaymentCreate(amount=10.99, sender_id=1, receiver_id=2)

# transaction_create = TransactionCreate(payment_id=1, status="pending")
# print(transaction_create)  # Output: TransactionCreate(payment_id=1, status='pending')