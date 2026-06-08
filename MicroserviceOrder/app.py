from fastapi import FastAPI  # FastAPI app for order service, equivalent to Spring Boot microservice app
from pydantic import BaseModel  # Pydantic model for registration payload to Eureka-like registry
import httpx  # HTTP client used to register service on startup

class ServiceRegistration(BaseModel):  # Model for service registry payload
    name: str  # Service name, as used by the Eureka server
    url: str  # Host or base URL for this service
    port: int  # Port number for this service

app = FastAPI(title="MicroserviceOrder")  # Order service application startup
EUREKA_URL = "http://127.0.0.1:8761"  # Eureka server location for discovery and registration
SERVICE_NAME = "MICROSERVICEORDER"  # Service ID used by Spring Cloud Gateway and Eureka
SERVICE_PORT = 8082  # Port that this order service listens on, equivalent to server.port in Spring Boot

@app.on_event("startup")  # Register this service with the Eureka-like registry at startup
async def register_with_registry():
    registration = ServiceRegistration(name=SERVICE_NAME, url="127.0.0.1", port=SERVICE_PORT)  # Build registration payload
    async with httpx.AsyncClient() as client:  # HTTP client to send registration request
        await client.post(f"{EUREKA_URL}/register", json=registration.dict())  # Send registration to registry

@app.get("/orders/{user_id}")  # Order endpoint analogous to Spring Boot OrderController
async def get_user_orders(user_id: str):
    return f"ORDER-1, ORDER-2, ORDER-3 - for user {user_id}"  # Return fixed order data like the Java controller
