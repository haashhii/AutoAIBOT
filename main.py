from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from langchain_openai import ChatOpenAI
from langchain.prompts import MessagesPlaceholder
from langchain.agents.openai_functions_agent.base import create_openai_functions_agent,OpenAIFunctionsAgent
from langchain.agents.openai_functions_agent.agent_token_buffer_memory import AgentTokenBufferMemory
from langchain.agents import AgentExecutor
from langchain.schema.messages import SystemMessage
from pydantic import BaseModel, Field
from tools_custom import StructuredTool
import os
import uuid
import csv
from langchain.callbacks.manager import AsyncCallbackManager
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates") 


class UserDataManager:
    def __init__(self, file_name="user_data.csv"):
        self.file_name = file_name
        self.create_csv_file()

    def create_csv_file(self):
        if not os.path.exists(self.file_name):
            with open(self.file_name, mode="w", newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["session_id", "user_name", "contact_number", "car_name"])  # Headers

    def save_user_data(self, session_id, user_name, contact_number, car_name=None):
        existing_data = self.load_existing_data()

        if session_id in existing_data:
            # For writing mulitple interset in the car
            current_cars = existing_data[session_id]['car_name']
            if car_name and car_name not in current_cars:
                current_cars.append(car_name)
            existing_data[session_id]['car_name'] = current_cars
        else:
            existing_data[session_id] = {
                'user_name': user_name,
                'contact_number': contact_number,
                'car_name': [car_name] if car_name else []
            }

        self.save_to_csv(existing_data)

    def load_existing_data(self):
        existing_data = {}
        if os.path.exists(self.file_name):
            with open(self.file_name, mode="r") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    car_names = row["car_name"].strip("[]").replace("'", "").split(", ")
                    existing_data[row["session_id"]] = {
                        "user_name": row["user_name"],
                        "contact_number": row["contact_number"],
                        "car_name": car_names if car_names[0] else []  
                    }
        return existing_data

    def save_to_csv(self, data):
        with open(self.file_name, mode="w", newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["session_id", "user_name", "contact_number", "car_name"])  # Write header
            for session_id, info in data.items():
                # Join the car names into a comma-separated string
                car_names_str = ', '.join(info["car_name"])
                writer.writerow([
                    session_id, 
                    info["user_name"], 
                    info["contact_number"], 
                    car_names_str  # Write as a clean string
                ])

class UserDataManagerService:
    def __init__(self, file_name="user_data_service.csv"):
        self.file_name = file_name
        self.create_csv_file()

    def create_csv_file(self):
        if not os.path.exists(self.file_name):
            with open(self.file_name, mode="w", newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["session_id", "user_name", "contact_number", "service_detail"])  # Headers

    def save_user_data(self, session_id, user_name, contact_number, service_detail=None):
        existing_data = self.load_existing_data()

        if session_id in existing_data:
            # For writing mulitple interset in the car
            current_service = existing_data[session_id]['service_detail']
            if service_detail and service_detail not in current_service:
                current_service.append(service_detail)
            existing_data[session_id]['service_detail'] = current_service
        else:
            existing_data[session_id] = {
                'user_name': user_name,
                'contact_number': contact_number,
                'service_detail': [service_detail] if service_detail else []
            }

        self.save_to_csv(existing_data)

    def load_existing_data(self):
        existing_data = {}
        if os.path.exists(self.file_name):
            with open(self.file_name, mode="r") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    car_names = row["service_detail"].strip("[]").replace("'", "").split(", ")
                    existing_data[row["session_id"]] = {
                        "user_name": row["user_name"],
                        "contact_number": row["contact_number"],
                        "service_detail": car_names if car_names[0] else []  
                    }
        return existing_data

    def save_to_csv(self, data):
        with open(self.file_name, mode="w", newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["session_id", "user_name", "contact_number", "service_detail"])  # Write header
            for session_id, info in data.items():
                # Join the car names into a comma-separated string
                car_names_str = ', '.join(info["service_detail"])
                writer.writerow([
                    session_id, 
                    info["user_name"], 
                    info["contact_number"], 
                    car_names_str  # Write as a clean string
                ])



user_data_manager = UserDataManager()
user_data_manager_service = UserDataManagerService()


def generate_session_id():
    return str(uuid.uuid4())


# session_id_2 = generate_session_id()

def general_inquiry(user_name: str, contact_number: str,car_intrested:str):
    user_data_manager.save_user_data(global_session_id, user_name, contact_number,car_intrested)
    return f"User {user_name} with contact number {contact_number}."



class VehicleRequest(BaseModel):
    car_name: str = Field(..., description="The name of the car the customer is asking about.")

llm = ChatOpenAI(
    openai_api_key=os.environ["OPENAI_API_KEY"], 
    model_name=os.environ["OPENAI_LLM_MODEL"], 
    temperature=0.2,
    streaming=True,
    callbacks=AsyncCallbackManager([])
)


system_message = SystemMessage(
    content=(
        
        # "You are a Customer Support Assistant Automobile company name as Hasham automobile company. Greet with the company and then ask other query."
        # "First Ask Customers Name and Contact Details, then check if user give his data otherwise ask him again."
        # "Always invoke general_inquiry when you get name, contact details, and car name or model."
        # "After that Invoke Vehicle_database chain and check if the car is available and if not apologize."
        # "Always invoke again general_inquiry whenever user mention again about any other car. "      
        """You are a Customer Support Assistant for Hashim Automobile Company. Start by greeting the customer with the company's name and then proceed to ask about their query.

        First, ask for the customer's name and contact details. If the customer does not provide this information, kindly ask again.

        Once you have the name, contact details, and the car model or brand or service the customer is interested in, invoke the general_inquiry or service_based_query process.


        If user show interset in Purchasing car Invoke the Vehicle_database process to check if the car is available. If it is not, apologize to the customer.

        When you get json in answer from the vehicle_database make it generalized to feel like human answer.

        Whenever the customer mentions another car, always invoke the general_inquiry process again."""
                
    )
)
def Servicedetailfunction(user_name: str, contact_number: str,service:str):
    user_data_manager_service.save_user_data(global_session_id, user_name, contact_number,service)
    return f"User {user_name} with contact number {contact_number}."

def vehicle_database(car_name:str):
    # car_data = '''[
    #     {
    #         "make": "Flibber",
    #         "model": "ZX99-Panda",
    #         "engine_capacity": "812cc",
    #         "year": "20XX",
    #         "color": "Blurple",
    #         "price": "$12,34O.99",
    #         "transmission": "FlimsyShift-4",
    #         "mileage": "One hundred thousand km"
    #     },
    #     {
    #         "make": "Yantro",
    #         "model": "Falcon-XT12",
    #         "engine_capacity": "1500qwe",
    #         "year": "201X",
    #         "color": "Sunset Rainbow",
    #         "price": "12O,999 Yen",
    #         "transmission": "Auto-ish",
    #         "mileage": "9999999km"
    #     }
    # ]'''
    # return car_data
    file_path = "car_Data.json"
    with open(file_path, 'r') as file:
        data = json.load(file)
    # Process the request object to extract the ca r name
    car_list = data.get("Sheet1", [])
    
    # Process the request to extract the car name
    for car in car_list:
        if car_name.lower() in car["make"].lower() or car_name.lower() in car["model"].lower():
            return car
    
    return {"error": "Car not found, apologize to the customer."}


class GeneralInquiryRequest(BaseModel):
    user_name: str = Field(..., description="The name of the customer.")
    contact_number: str = Field(..., description="The contact number of the customer.")
    car_intrested: str = Field(..., description="Car model in which user is intersted.")


class ServiceDetail(BaseModel):
    user_name: str = Field(..., description="The name of the customer.")
    contact_number: str = Field(..., description="The contact number of the customer.")
    service: str = Field(..., description="The service customer want i.g changing oil and any service related to car")


tools = [
    StructuredTool.from_function(
        name="general_inquiry",
        func=general_inquiry,
        description="Invoke this tool when user provides their name and number.",
        args_schema=GeneralInquiryRequest,  
    ),
    StructuredTool.from_function(
        name="vehicle_database",
        func=vehicle_database,
        description="Invoke this tool when you need data about a vehicle by name",
        args_schema=VehicleRequest,
    ),
    StructuredTool.from_function(
        name="service_based_query",
        func=Servicedetailfunction,
        description="Invoke this tool when you user give information about which service he want.",
        args_schema=ServiceDetail,
    )
]


memory_key = "history"
memory = AgentTokenBufferMemory(memory_key=memory_key, llm=llm, max_token_limit=700)


prompt = OpenAIFunctionsAgent.create_prompt(
    system_message=system_message,
    extra_prompt_messages=[MessagesPlaceholder(variable_name=memory_key)]
)


agent = create_openai_functions_agent(llm=llm, tools=tools, prompt=prompt)

# Agent Executor
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    memory=memory,
    verbose=True,
    return_intermediate_steps=True,
    handle_parsing_errors="Check your output and make sure it conforms, use the Action/Action Input syntax"
)

@app.get("/", response_class=HTMLResponse)
async def get_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# @app.post("/process")
# async def process_user_input(request: Request, name: str = Form(...), contact: str = Form(...), car_name: str = Form(...)):
#     session_id = generate_session_id()
#     user_data_manager.save_user_data(session_id, name, contact, car_name)
#     response = await agent_executor.ainvoke({"input": f"User: {name}, Contact: {contact}, Car: {car_name}"})
#     return {"response": response["output"]}



def generate_session_id():
    return str(uuid.uuid4())
# session_id_2 = generate_session_id()

@app.get("/session")
async def get_session_id():
    return {"session_id": generate_session_id()}

global_session_id = ''

@app.post("/chat/{session_id}")
async def chat_with_user(session_id: str, request: Request):
    global global_session_id
    global_session_id = session_id
    user_input = await request.json()
    # session_id_2 = generate_session_id() 
    message = user_input.get('message')

    
    response = await agent_executor.ainvoke({"input": message})
    
    return {"response": response["output"]}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)


