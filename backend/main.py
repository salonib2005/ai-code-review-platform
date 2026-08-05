from fastapi import FastAPI

app = FastAPI(
    title="AI Code Review Platform",
    version="1.0.0"
)


@app.get("/")
def home():
    return {
        "status": "running",
        "message": "AI Code Review Platform Backend 🚀"
    }