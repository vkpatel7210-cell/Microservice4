from fastapi import FastAPI, HTTPException  # Spring Boot @SpringBootApplication equivalent and HTTP handling
from pydantic import BaseModel  # Spring Boot uses POJOs / DTOs for payloads, here we use Pydantic models
from typing import Dict, List  # Use typing for the in-memory registry collection

class ServiceRegistration(BaseModel):  # Model for service registration requests, similar to Eureka instance info
    name: str  # Service name like MICROSERVICEUSER or MICROSERVICEORDER
    url: str  # Base URL or host of the service
    port: int  # Port where the service is listening

app = FastAPI(title="MicroserviceEurekaServer")  # FastAPI app acts like SpringApplication.run

service_registry: Dict[str, List[str]] = {}  # In-memory registry like Eureka server instance registry

@app.post("/register")  # Registration endpoint for services, similar to Eureka client registration
async def register_service(registration: ServiceRegistration):
    upper_name = registration.name.upper()  # Normalize service names, similar to Spring Cloud service IDs
    instance_url = f"{registration.url}:{registration.port}"  # Build the instance URL for the registry
    service_registry.setdefault(upper_name, []).append(instance_url)  # Store new instance in registry
    return {"status": "registered", "service": upper_name, "instances": service_registry[upper_name]}  # Return registration result

@app.get("/services/{service_name}")  # Eureka-style discovery endpoint for a single service name
async def get_service(service_name: str):
    upper_name = service_name.upper()  # Normalize service names to uppercase for lookup
    instances = service_registry.get(upper_name)  # Lookup instances from the registry
    if not instances:  # If no instances are registered, return 404 like Eureka not found
        raise HTTPException(status_code=404, detail="Service not found")
    return {"service": upper_name, "instances": instances}  # Return available instances

@app.get("/services")  # Endpoint to list all registered services, useful for debugging like Eureka dashboard
async def list_services():
    return {"registry": service_registry}  # Return the entire in-memory registry
