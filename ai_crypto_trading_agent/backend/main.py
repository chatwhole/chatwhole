from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class SignalRequest(BaseModel):
    symbol: str
    market_data: dict
    sentiment_score: float

@app.post("/api/generate_signal")
async def generate_signal(data: SignalRequest):
    # Placeholder logic for signal generation
    forecast = data.market_data.get("forecast", 0)
    current_price = data.market_data.get("current_price", 0)
    sentiment = data.sentiment_score

    if forecast > current_price and sentiment > 0.5:
        action = "BUY"
    elif forecast < current_price and sentiment < -0.5:
        action = "SELL"
    else:
        action = "HOLD"

    return {"symbol": data.symbol, "action": action}

class TradeExecutionRequest(BaseModel):
    symbol: str
    action: str
    quantity: float

@app.post("/api/execute_trade")
async def execute_trade(data: TradeExecutionRequest):
    # Placeholder for trade execution via Binance API
    return {"symbol": data.symbol, "action": data.action, "quantity": data.quantity, "status": "executed"}

@app.get("/")
async def root():
    return {"message": "AI Crypto Trading Agent Backend is running."}
