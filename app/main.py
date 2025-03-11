from fastapi import FastAPI
from app.routes.routes import router

app = FastAPI(title="Drug-Drug Interaction API")

app.include_router(router, tags=["Main"])

@app.get("/")
async def root():
    return {"message": "Drug-Drug Interaction API is running."}
