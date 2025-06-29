from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import convert, playlist, batch, status, download

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://127.0.0.1:8080"],  # <-- change to your frontend's origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "api is running"}

app.include_router(convert.router, prefix="/api")
app.include_router(playlist.router, prefix="/api")
app.include_router(batch.router, prefix="/api")
app.include_router(status.router, prefix="/api")
app.include_router(download.router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)