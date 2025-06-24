from pydantic import BaseModel, Field
from typing import Optional
from tools.user_data import UserDataManager  # ✅ make sure it's TinyDB-based

class GeneralInquiryRequest(BaseModel):
    user_name: str = Field(..., description="Customer name")
    contact_number: str = Field(..., description="Customer contact")
    car_intrested: str = Field(..., description="Car the user is interested in")

user_data_manager = UserDataManager()  # ✅ Instance of the TinyDB version

def general_inquiry(user_name: str, contact_number: str, car_intrested: str, session_id: str) -> str:
    user_data_manager.save_user_data(session_id, user_name, contact_number, car_intrested)
    return f"Thanks {user_name}! Your interest in {car_intrested} has been recorded."
