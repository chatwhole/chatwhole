from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class ProductListingRequest(BaseModel):
    product_name: str
    key_features: list[str]
    target_market: str
    tone: str

@app.post("/api/product_listing")
async def create_product_listing(data: ProductListingRequest):
    # Placeholder GPT-4o prompt simulation
    prompt = f"""
    You're an expert in e-commerce SEO. Create a high-converting product listing for:

    Product: {data.product_name}
    Key Features: {', '.join(data.key_features)}
    Target Market: {data.target_market}
    Tone: {data.tone}

    Include: Title, 5 bullet points, description (300 words), and meta keywords.
    """
    # Simulate GPT response
    listing = {
        "title": f"{data.product_name} - Best Quality & Features",
        "bullet_points": [
            "High quality and durable",
            "Eco-friendly materials",
            "Portable and lightweight",
            "Easy to use and maintain",
            "Affordable price"
        ],
        "description": f"This {data.product_name} is perfect for {data.target_market}. It offers {', '.join(data.key_features)}. Buy now to enjoy the benefits!",
        "meta_keywords": data.key_features + [data.product_name, "e-commerce", "best product"]
    }
    return {"prompt": prompt, "listing": listing}

class InventoryRequest(BaseModel):
    sku: str
    current_stock: int
    sales_velocity_60d: int

@app.post("/api/inventory")
async def manage_inventory(data: InventoryRequest):
    # Placeholder logic for reorder suggestion
    reorder = data.current_stock < data.sales_velocity_60d * 0.2
    return {"sku": data.sku, "reorder_needed": reorder}

class AdCampaignRequest(BaseModel):
    campaign_name: str
    platform: str
    budget: float
    target_audience: str

@app.post("/api/ad_campaign")
async def create_ad_campaign(data: AdCampaignRequest):
    # Placeholder GPT-4o prompt simulation
    prompt = f"Create an ad campaign for {data.campaign_name} on {data.platform} targeting {data.target_audience} with a budget of ${data.budget}."
    ad_copy = f"Buy {data.campaign_name} now! Best deal for {data.target_audience}."
    return {"prompt": prompt, "ad_copy": ad_copy}

@app.get("/")
async def root():
    return {"message": "AI E-commerce Operations Agent Backend is running."}
