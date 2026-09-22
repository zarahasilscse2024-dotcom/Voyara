from typing import Any
from datetime import date
from pydantic import BaseModel, EmailStr, Field

class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    phone: str = Field(min_length=7, max_length=30)
    password: str = Field(min_length=8, max_length=128)
    confirm_password: str
    role: str = "traveler"

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    role: str = "traveler"

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    password: str = Field(min_length=8, max_length=128)
    confirm_password: str

class ReviewRequest(BaseModel):
    package_id: str
    rating: int = Field(ge=1, le=5)
    text: str = Field(min_length=5, max_length=1000)

class BookingRequest(BaseModel):
    package_id: str
    travel_date: date
    travelers: int = Field(ge=1, le=50)
    name: str
    email: EmailStr
    phone: str
    special_requests: str = ""

class ProfileUpdateRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    phone: str = Field(min_length=7, max_length=30)

class PaymentOrderRequest(BaseModel):
    booking_id: str

class PaymentVerifyRequest(BaseModel):
    booking_id: str
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str

class PreferenceRequest(BaseModel):
    budget: float = Field(gt=0)
    budget_min: float = 0
    budget_max: float = 0
    destination: str = ""
    travel_type: str = ""
    duration: int = Field(ge=1, le=60)
    interests: list[str] = []
    adventure_level: str = ""
    group_type: str = ""

class ChatMessage(BaseModel):
    role: str
    content: str = Field(min_length=1, max_length=2000)

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1000)
    conversation: list[ChatMessage] = Field(default_factory=list, max_length=20)

class PackageRequest(BaseModel):
    name: str
    destination: str
    description: str
    price: float = Field(gt=0)
    duration: int = Field(gt=0)
    category: str
    images: list[str] = []
    itinerary: list[dict[str, Any]] = []
    accommodation: str = ""
    transport: str = ""
    meals: str = ""
    activities: list[str] = []
    included: list[str] = []
    excluded: list[str] = []
    cancellation_policy: str = "Free cancellation up to 7 days before departure."
