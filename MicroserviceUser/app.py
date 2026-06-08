from fastapi import FastAPI, HTTPException  # FastAPI app for user service, equivalent to Spring Boot microservice app
from pydantic import BaseModel  # Model for service registry payload
import httpx  # HTTP client to resolve order service via registry

class ServiceRegistration(BaseModel):  # Payload model for service registration
    name: str  # Service name for Eureka registration
    url: str  # Host or URL for this service instance
    port: int  # Port where this service is listening

app = FastAPI(title="MicroserviceUser")  # User service application initialization
EUREKA_URL = "http://127.0.0.1:8761"  # Registry server URL, like Eureka client configuration in Spring
SERVICE_NAME = "MICROSERVICEUSER"  # Service ID for this user service
SERVICE_PORT = 8081  # Port this user service listens on, analogous to server.port in Spring Boot

@app.on_event("startup")  # Register user service with registry when the app starts
async def register_with_registry():
    registration = ServiceRegistration(name=SERVICE_NAME, url="127.0.0.1", port=SERVICE_PORT)  # Build registration payload for registry
    async with httpx.AsyncClient() as client:  # Use HTTP client to call registry
        await client.post(f"{EUREKA_URL}/register", json=registration.dict())  # Register this service instance with Eureka-like registry

async def resolve_service(service_name: str) -> str:  # Resolve a downstream service URL from the registry
    async with httpx.AsyncClient() as client:  # HTTP client similar to RestTemplate load-balanced calls
        response = await client.get(f"{EUREKA_URL}/services/{service_name}")  # Query registry for service instances
    if response.status_code != 200:  # If service is not found, raise an exception
        raise HTTPException(status_code=502, detail=f"Service {service_name} unavailable")
    instances = response.json().get("instances", [])  # Read the list of instances from registry response
    if not instances:  # If no instances are available, return a gateway-style error
        raise HTTPException(status_code=502, detail=f"No instances for {service_name}")
    return instances[0]  # Return first instance URL for calling downstream service

@app.get("/user/{user_id}")  # User endpoint equivalent to Spring Boot UserController
async def get_user_orders(user_id: str):
    order_instance = await resolve_service("MICROSERVICEORDER")  # Discover order service via registry, like RestTemplate with load balancer
    async with httpx.AsyncClient() as client:  # Create HTTP client to call the order service
        response = await client.get(f"http://{order_instance}/orders/{user_id}")  # Call the order service endpoint
    if response.status_code != 200:  # If the order service returns an error, propagate it
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return f"User Orders ({user_id}) : {response.text}"  # Return the combined user/order response like the Java controller
