from fastapi import FastAPI, Request, HTTPException
from starlette.responses import JSONResponse
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import sys
import asyncio
from starlette.middleware.cors import CORSMiddleware
from services.databases.postgres.connections import AsyncDBPoolSingleton
from routes.risk_routes import router as risks
from routes.risk_responses_routes import router as risk_responses
from routes.risk_ratings_routes import router as risk_ratings
from routes.risk_kri_routes import router as risk_kri
from routes.activity_routes import router as activities
from routes.rmp_routes import router as rmp
from routes.risk_register_routes import router as risk_registers
from routes.user_routes import router as risk_users
from routes.activity_reports_routes import router as activity_reports



load_dotenv()

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

@asynccontextmanager
async def lifespan(_api: FastAPI):
    try:
        pool_instance = AsyncDBPoolSingleton.get_instance()
        await pool_instance.get_pool()
    except Exception as e:
        print(e)

    yield

    try:
        pool_instance = AsyncDBPoolSingleton.get_instance()
        if pool_instance:
            await pool_instance.close_pool()

    except Exception as e:
        print(e)

app = FastAPI(lifespan=lifespan)

# noinspection PyTypeChecker
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    """
    Middleware to globally catch and handle exceptions during HTTP request processing.

    This middleware intercepts all HTTP requests and ensures that any unhandled
    exceptions are caught and returned as standardized JSON responses. It allows
    `HTTPException` to propagate normally so that FastAPI's built-in or custom
    exception handlers can process them. Any other unhandled exceptions are caught
    and returned as a 500 Internal Server Error with a JSON response containing
    the exception message.

    Args:
        request (Request): The incoming HTTP request.
        call_next (Callable): A function that forwards the request to the next middleware
                              or endpoint handler.

    Returns:
        Response: The HTTP response returned by the next middleware/handler or a JSON
                  response in case of unhandled exceptions.
    """
    try:
        response = await call_next(request)
        return response

    except HTTPException as h:
        raise h

    except Exception as e:
        print(e)
        return JSONResponse(
            status_code=500,
            content={"detail": str(e)}
        )


@app.get("/")
async def home():
    return "Hello world"

app.include_router(risks, tags=["Risks Router"])
app.include_router(risk_responses, tags=["Risks Responses Router"])
app.include_router(risk_ratings, tags=["Risks Ratings Router"])
app.include_router(risk_kri, tags=["Risks KRI Router"])
app.include_router(activities, tags=["Activities Router"])
app.include_router(rmp, tags=["Risk Management Plan Router"])
app.include_router(risk_registers, tags=["Risk Register Router"])
app.include_router(risk_users, tags=["Risk Users Router"])
app.include_router(activity_reports, tags=["Activity Reports Router"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
