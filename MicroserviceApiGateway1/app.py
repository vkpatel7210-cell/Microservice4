from fastapi import FastAPI, HTTPException  # FastAPI gateway app analogous to Spring Cloud Gateway app
from fastapi.responses import PlainTextResponse  # Use plain text for simple routed responses
from httpx import AsyncClient  # Use HTTP client similar to RestTemplate or WebClient in Spring

app = FastAPI(title="MicroserviceApiGateway1")  # API gateway application initialization
EUREKA_URL = "http://127.0.0.1:8761"  # Hard-coded Eureka server URL, like Eureka client configuration

async def resolve_service(service_name: str) -> str:  # Resolve a service name through registry, analog to load-balanced discovery
    async with AsyncClient() as client:  # Create an async HTTP client similar to Spring WebClient
        response = await client.get(f"{EUREKA_URL}/services/{service_name}")  # Query Eureka for available instances
    if response.status_code != 200:  # If registry lookup fails, raise an HTTP exception
        raise HTTPException(status_code=502, detail=f"Service {service_name} unavailable")
    instances = response.json().get("instances", [])  # Parse instance list from registry response
    if not instances:  # If no instances are registered, return bad gateway
        raise HTTPException(status_code=502, detail=f"No instances for {service_name}")
    return instances[0]  # Return first instance, simulating basic load balancing

async def proxy_request(path: str, service_name: str) -> PlainTextResponse:  # Forward requests to downstream services
    instance_url = await resolve_service(service_name)  # Resolve service instance from registry
    target_url = f"http://{instance_url}/{path.lstrip('/')}"  # Build proxied URL, preserving request path
    async with AsyncClient() as client:  # Use HTTP client to call the downstream service
        response = await client.get(target_url)  # Forward GET request to downstream service
    if response.status_code != 200:  # If downstream service returns an error, propagate a gateway error
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return PlainTextResponse(content=response.text, status_code=response.status_code)  # Return downstream response body

@app.get("/user/{user_id}")  # Gateway route for user service, equivalent to spring.cloud.gateway.routes[0]
async def gateway_user(user_id: str):
    return await proxy_request(f"user/{user_id}", "MICROSERVICEUSER")  # Route /user/** to MICROSERVICEUSER via registry and proxy

@app.get("/orders/{user_id}")  # Gateway route for order service, equivalent to spring.cloud.gateway.routes[1]
async def gateway_orders(user_id: str):
    return await proxy_request(f"orders/{user_id}", "MICROSERVICEORDER")  # Route /orders/** to MICROSERVICEORDER via registry and proxy

@app.get("/health")  # Health endpoint for gateway, similar to actuator health endpoints in Spring Boot
async def health_check():
    return {"status": "UP", "service": "MicroserviceApiGateway1"}  # Basic health response
