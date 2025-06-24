from pydantic import BaseModel, Field
from tools.user_data import UserDataManagerService

# Pydantic schema for service-based tool input
class ServiceDetail(BaseModel):
    user_name: str = Field(..., description="Name of the user.")
    contact_number: str = Field(..., description="User's contact number.")
    service_detail: str = Field(..., description="The service the user is interested in.")

# Initialize the service data manager
user_data_manager_service = UserDataManagerService()

# Tool function used by LangChain agent
def Servicedetailfunction(user_name: str, contact_number: str, service_detail: str, session_id: str) -> str:
    user_data_manager_service.save_service_data(session_id, user_name, contact_number, service_detail)
    return f"Thanks {user_name}, we’ve noted your interest in the '{service_detail}' service."

# Optional utilities for debugging or admin tools
def get_services_for_session(session_id: str) -> dict:
    service = user_data_manager_service.get_service_by_session(session_id)
    return service or {"message": "No service data found for this session."}

def get_all_service_requests() -> list:
    return user_data_manager_service.get_all_services()
