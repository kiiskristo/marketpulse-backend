from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .crew import HowDoYouFindMeCrew
from .clean_json import clean_and_parse_json

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
        # 1) Run the pipeline
        crew_instance = HowDoYouFindMeCrew()
        result = crew_instance.crew().kickoff(inputs={'query': request.query})

        # 2) Clean/parse 'raw' JSON in each task result
        for task_output in result.get("tasks_output", []):
            if "raw" in task_output:
                try:
                    parsed_json = clean_and_parse_json(task_output["raw"])
                    task_output["parsed"] = parsed_json
                except ValueError as e:
                    task_output["parse_error"] = str(e)
                    task_output["parsed"] = None
        
        # 3) Return the entire result (including "parsed" data)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))