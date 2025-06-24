#tools/user_data.py

import os
from tinydb import TinyDB, Query
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware

# Setup database paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data")
os.makedirs(DATA_DIR, exist_ok=True)

CAR_DB_PATH = os.path.join(DATA_DIR, "car_inquiries.json")
SERVICE_DB_PATH = os.path.join(DATA_DIR, "service_requests.json")


def init_db(path):
    return TinyDB(path, storage=CachingMiddleware(JSONStorage))

# Common query object
User = Query()

# === Car Inquiry Manager ===
class UserDataManager:
    """Handles car inquiries."""
    def __init__(self):
        self.db = init_db(CAR_DB_PATH)

    def save_user_data(self, session_id: str, user_name: str, contact_number: str, car_intrested: str):
        existing = self.db.get(User.session_id == session_id)
        if existing:
            self.db.update({"car_intrested": car_intrested}, User.session_id == session_id)
        else:
            self.db.insert({
                "session_id": session_id,
                "user_name": user_name,
                "contact_number": contact_number,
                "car_intrested": car_intrested
            })

    def get_user_data(self, session_id: str):
        return self.db.get(User.session_id == session_id)

    def clear_user_data(self, session_id: str):
        self.db.remove(User.session_id == session_id)

# === Service Request Manager ===
class UserDataManagerService:
    """Handles service-based queries."""
    def __init__(self):
        self.db = init_db(SERVICE_DB_PATH)

    def save_service_data(self, session_id: str, user_name: str, contact_number: str, service_detail: str):
        existing = self.db.get(User.session_id == session_id)
        if existing:
            updated = dict(existing)
            service_list = updated.get("service_detail", [])
            if service_detail not in service_list:
                service_list.append(service_detail)
            updated["service_detail"] = service_list
            self.db.update(updated, User.session_id == session_id)
        else:
            self.db.insert({
                "session_id": session_id,
                "user_name": user_name,
                "contact_number": contact_number,
                "service_detail": [service_detail]
            })

    def get_service_by_session(self, session_id: str):
        return self.db.get(User.session_id == session_id)

    def get_all_services(self):
        return self.db.all()

    def clear_service_data(self, session_id: str):
        self.db.remove(User.session_id == session_id)
