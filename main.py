from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import logging

from routes import main as main_routes

# Load environment variables from .env
load_dotenv()

# Configure logging
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Create FastAPI app instance
app = FastAPI()

# Enable CORS (allow requests from any origin for now)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Mount static file serving
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include the main API routes
app.include_router(main_routes.router)

# Run the app using uvicorn when called directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
