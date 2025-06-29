from fastapi import FastAPI
from api import convert, playlist, batch, status, download

app = FastAPI()

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