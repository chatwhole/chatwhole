from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings

app = FastAPI()

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize LangChain components
llm = ChatOpenAI(model="gpt-4o")
db = Chroma(persist_directory="docs_index", embedding_function=OpenAIEmbeddings())
qa = RetrievalQA.from_chain_type(llm=llm, retriever=db.as_retriever())

class QueryRequest(BaseModel):
    query: str

@app.post("/api/query")
async def query_agent(request: QueryRequest):
    response = qa.run(request.query)
    return {"answer": response}

@app.get("/")
async def root():
    return {"message": "AI Customer Support Agent Backend is running."}
