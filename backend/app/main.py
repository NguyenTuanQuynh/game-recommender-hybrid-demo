from fastapi import FastAPI

app = FastAPI(title="Hybrid Game Recommender API")

@app.get("/")
def root():
    return {"message": "Backend is running"}