from fastapi import FastAPI
from api.routers import students

app = FastAPI(title="畢業審查系統 API")


@app.get("/")
def root():
    return {"message": "畢業審查系統 API", "version": "1.0.0"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


app.include_router(students.router)
