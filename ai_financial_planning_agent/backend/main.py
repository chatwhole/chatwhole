from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests

app = FastAPI()

class BankAccountConnectRequest(BaseModel):
    public_token: str

class BudgetRequest(BaseModel):
    income: float
    spending: dict

@app.post("/api/connect_bank")
async def connect_bank(data: BankAccountConnectRequest):
    # Placeholder for Plaid token exchange and transaction fetch
    # In production, exchange public_token for access_token and fetch transactions
    return {"status": "connected", "public_token": data.public_token}

@app.post("/api/budget")
async def generate_budget(data: BudgetRequest):
    # Placeholder GPT-4o prompt simulation
    prompt = f"""
    You are a smart financial advisor.
    The user earns ${data.income}/month. Here's their categorized spending:
    """
    for category, amount in data.spending.items():
        prompt += f"\n- {category}: ${amount}"
    prompt += "\nGenerate a monthly budget that improves savings while preserving lifestyle."

    # Simulate GPT response
    budget_advice = "Based on your income and spending, consider reducing dining expenses by 10% and increasing savings by 15%."
    return {"prompt": prompt, "budget_advice": budget_advice}

@app.get("/")
async def root():
    return {"message": "AI Financial Planning Agent Backend is running."}
