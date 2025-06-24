# app_context.py

import os
import json
from functools import partial
from typing import Union
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor
from langchain.agents.openai_functions_agent.base import create_openai_functions_agent, OpenAIFunctionsAgent
from langchain.agents.openai_functions_agent.agent_token_buffer_memory import AgentTokenBufferMemory
from langchain.schema.messages import SystemMessage
from langchain.prompts import MessagesPlaceholder
from langchain.callbacks.manager import AsyncCallbackManager
from pydantic import BaseModel, Field

from tools_custom import StructuredTool
from tools.user_data import UserDataManager, UserDataManagerService

# === Load Environment Variables ===
load_dotenv()

# === Initialize User Data Managers ===
user_data_manager = UserDataManager()
user_data_manager_service = UserDataManagerService()

# === In-memory Session-Specific Memory Store ===
memory_store = {}

# === Tool Functions ===

def general_inquiry(user_name: str, contact_number: str, car_intrested: str, session_id: str) -> str:
    user_data_manager.save_user_data(session_id, user_name, contact_number, car_intrested=car_intrested)
    return f"User {user_name} with contact number {contact_number} and car interest in {car_intrested} logged."

def service_detail_function(user_name: str, contact_number: str, service: str, session_id: str) -> str:
    user_data_manager_service.save_service_data(session_id, user_name, contact_number, service)
    return f"Thanks {user_name}, we’ve noted your interest in the '{service}' service."

def vehicle_database(car_name: str) -> Union[dict, str]:
    try:
        with open("data", "car_Data.json") as file:
            data = json.load(file)
    except Exception as e:
        return {"error": str(e)}

    car_list = data.get("Sheet1", [])
    car_name = car_name.lower().strip()
    for car in car_list:
        make = car.get("make", "").lower()
        model = car.get("model", "").lower()
        if car_name in model or car_name in make or car_name in f"{make} {model}":
            return {
                "make": car.get("make"),
                "model": car.get("model"),
                "year": car.get("year"),
                "price": f"${car.get('retail_price')}",
                "body_type": car.get("body_type"),
                "fuel_type": car.get("fuel_type"),
                "drivetrain": car.get("drivetrain"),
                "interior": car.get("interior"),
                "exterior": car.get("exterior"),
                "vehicle_type": car.get("vehicle_type", "Used"),
                "description": (
                    f"{car.get('year')} {car.get('make')} {car.get('model')} "
                    f"({car.get('trim')}), {car.get('body_type')}, "
                    f"{car.get('fuel_type')} with {car.get('drivetrain')} drivetrain. "
                    f"Interior: {car.get('interior')}, Exterior: {car.get('exterior')}."
                )
            }
    return f"Sorry, we couldn't find any vehicle matching '{car_name}'."

# === Pydantic Schemas ===

class VehicleRequest(BaseModel):
    car_name: str = Field(..., description="Car name to search for.")

class GeneralInquiryRequest(BaseModel):
    user_name: str = Field(..., description="Name of the user.")
    contact_number: str = Field(..., description="Contact number of the user.")
    car_intrested: str = Field(..., description="Car the user is interested in.")

class ServiceDetail(BaseModel):
    user_name: str = Field(..., description="Name of the user.")
    contact_number: str = Field(..., description="Contact number of the user.")
    service: str = Field(..., description="Service the user is interested in.")

# === System Prompt ===

system_message = SystemMessage(
    content="You are a Customer Support Assistant for Hashim Automobile Company. "
            "Greet the customer, ask for details, and assist with inquiries, vehicle availability, or service-related information."
)

# === LLM Initialization ===

llm = ChatOpenAI(
    openai_api_key=os.environ["OPENAI_API_KEY"],
    model_name=os.environ["OPENAI_LLM_MODEL"],
    temperature=0.2,
    streaming=True,
    callbacks=AsyncCallbackManager([])
)

# === Tool Registry ===

def get_tools_for_session(session_id: str):
    return [
        StructuredTool.from_function(
            name="general_inquiry",
            func=partial(general_inquiry, session_id=session_id),
            description="Capture user details for car inquiries.",
            args_schema=GeneralInquiryRequest,
        ),
        StructuredTool.from_function(
            name="vehicle_database",
            func=vehicle_database,
            description="Fetch vehicle info based on model/make.",
            args_schema=VehicleRequest,
        ),
        StructuredTool.from_function(
            name="service_based_query",
            func=partial(service_detail_function, session_id=session_id),
            description="Log service-related user interest.",
            args_schema=ServiceDetail,
        )
    ]

# === Agent Executor Factory ===

def get_agent_executor(session_id: str) -> AgentExecutor:
    if session_id not in memory_store:
        memory_store[session_id] = AgentTokenBufferMemory(
            memory_key="history",
            llm=llm,
            max_token_limit=700
        )

    tools = get_tools_for_session(session_id)

    prompt = OpenAIFunctionsAgent.create_prompt(
        system_message=system_message,
        extra_prompt_messages=[MessagesPlaceholder(variable_name="history")]
    )

    agent = create_openai_functions_agent(llm=llm, tools=tools, prompt=prompt)

    return AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory_store[session_id],
        verbose=True,
        return_intermediate_steps=True,
        handle_parsing_errors="Check your output and ensure it matches the expected format."
    )
