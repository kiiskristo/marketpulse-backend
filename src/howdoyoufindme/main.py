# src/howdoyoufindme/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .crew import HowDoYouFindMeCrew
import warnings

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://kiiskristo.github.io"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchRequest(BaseModel):
    query: str

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/api/search-rank")
async def search_rank(request: SearchRequest):
    try:
        crew = HowDoYouFindMeCrew()
        result = crew.crew().kickoff(inputs={'query': request.query})
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Keep the CLI functions but move them to a separate file
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)