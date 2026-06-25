import chromadb
from src.config_loader import APP_CONFIG,PROMPTS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import CrossEncoder
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv
load_dotenv()


#chromadb
chroma_native_client=chromadb.PersistentClient(
    path=APP_CONFIG["chroma"]["path"]
)
collection = chroma_native_client.get_or_create_collection(
    name=APP_CONFIG["chroma"]["collection_name"]
)

#text_splitter
text_splitter=RecursiveCharacterTextSplitter(
        chunk_size=APP_CONFIG["chunking"]["chunk_size"],
        chunk_overlap=APP_CONFIG["chunking"]["chunk_overlap"]
)
#reranker
reranker=CrossEncoder(    
    APP_CONFIG["reranker"]["model_name"]
)

#llm
groq_api_key=os.getenv("GROQ_API_KEY")
llm=ChatGroq(
    model=APP_CONFIG["llm"]["model_name"],
    groq_api_key=groq_api_key,
    temperature=APP_CONFIG["llm"]["temperature"],
    streaming=APP_CONFIG["llm"]["streaming"]
)
top_n_context=APP_CONFIG["reranker"]["top_n_context"]

prompt_template = PROMPTS["rag"]["system_prompt"]
intent_prompt= PROMPTS["rag"]["intent_prompt"]
