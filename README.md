# FastAPI Conversion of Spring Boot Microservices

This workspace contains four Python FastAPI services converted from the Spring Boot microservice setup:

- `MicroserviceEurekaServer` - registry service equivalent to Spring Cloud Eureka server
- `MicroserviceApiGateway1` - API gateway equivalent to Spring Cloud Gateway routes
- `MicroserviceOrder` - Order microservice equivalent to Spring Boot order service
- `MicroserviceUser` - User microservice equivalent to Spring Boot user service

Each `app.py` file includes inline comments that compare the FastAPI implementation with the Spring Boot original.

## Install dependencies

```bash
python -m pip install -r requirements.txt
```

## Run services in startup order

1. Start the registry server:
   ```bash
   uvicorn MicroserviceEurekaServer.app:app --host 127.0.0.1 --port 8761 --reload
   ```
2. Start the order service:
   ```bash
   uvicorn MicroserviceOrder.app:app --host 127.0.0.1 --port 8082 --reload
   ```
3. Start the user service:
   ```bash
   uvicorn MicroserviceUser.app:app --host 127.0.0.1 --port 8081 --reload
   ```
4. Start the gateway service:
   ```bash
   uvicorn MicroserviceApiGateway1.app:app --host 127.0.0.1 --port 8080 --reload
   ```

## Example requests

- User service via gateway: `http://127.0.0.1:8080/user/123`
- Order service via gateway: `http://127.0.0.1:8080/orders/123`

## Notes

- This conversion preserves the same number of microservices as the Spring Boot example.
- The registry server is intentionally minimal and in-memory, providing the same discovery concept as Eureka.
- The gateway uses service discovery and request forwarding to mimic Spring Cloud Gateway routes.
