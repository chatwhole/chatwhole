from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class ContractReviewRequest(BaseModel):
    contract_text: str
    jurisdiction: str

@app.post("/api/contract_review")
async def contract_review(data: ContractReviewRequest):
    # Placeholder GPT-4o prompt simulation
    prompt = f"""
    You are a legal expert.

    Review the following contract clause and flag any red flags, suggest improvements, and explain their legal implications.

    Clause:
    {data.contract_text}

    Jurisdiction: {data.jurisdiction}
    """
    # Simulate GPT response
    review = {
        "flags": ["Potentially restrictive non-compete clause."],
        "suggestions": ["Consider limiting duration to 1 year."],
        "explanation": "Non-compete clauses longer than 1 year may be unenforceable in some jurisdictions."
    }
    return {"prompt": prompt, "review": review}

class ClauseLibraryRequest(BaseModel):
    search_term: str

@app.post("/api/clause_library")
async def clause_library(data: ClauseLibraryRequest):
    # Placeholder clause search simulation
    clauses = [
        "Non-compete clause: Employee shall not compete for 1 year.",
        "Confidentiality clause: Employee shall keep information confidential."
    ]
    matched = [c for c in clauses if data.search_term.lower() in c.lower()]
    return {"search_term": data.search_term, "matched_clauses": matched}

class DocumentIngestionRequest(BaseModel):
    document_url: str

@app.post("/api/document_ingest")
async def document_ingest(data: DocumentIngestionRequest):
    # Placeholder document ingestion simulation
    return {"document_url": data.document_url, "status": "ingested"}

@app.get("/")
async def root():
    return {"message": "AI Legal Assistant Agent Backend is running."}
