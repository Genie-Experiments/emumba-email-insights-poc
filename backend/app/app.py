from fastapi import FastAPI
from api.v1.endpoints.query import queryRouter
from api.v1.endpoints.companies import companiesRouter
from fastapi.middleware.cors import CORSMiddleware
from config.Config import config
from middlewares.log_request_time import log_request_time
from middlewares.request_logging import RequestLoggingMiddleware
from db.database import Base, engine

app = FastAPI()
port = int(config.SERVER_PORT)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.middleware("http")(log_request_time)
app.add_middleware(RequestLoggingMiddleware)

app.include_router(queryRouter, prefix="/api/v1")
app.include_router(companiesRouter, prefix="/api/v1/companies")


@app.get("/")
async def get_health():
    return f"Server running on port {port}"


Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=port, workers=6, reload=False)
