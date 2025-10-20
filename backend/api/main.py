from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import students_router, rules_router, review_router, results_router

app = FastAPI(title="畢業審查系統 API")

# 設定 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:9000",  # Quasar dev server default port
        "http://127.0.0.1:9000",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "畢業審查系統 API", "version": "1.0.0"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


app.include_router(students_router.router,prefix="/api")
app.include_router(rules_router.router,prefix="/api")
app.include_router(review_router.router,prefix="/api")
app.include_router(results_router.router,prefix="/api")
