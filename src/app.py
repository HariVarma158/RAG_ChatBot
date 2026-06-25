from fastapi import FastAPI, File, UploadFile as UF, Query
from pypdf import PdfReader
from typing import Annotated,Optional
from src.config_loader import APP_CONFIG
import src.ingest as ing
import src.retriever as ret
import src.reranker as rerank
import src.utils as util
from pydantic import WithJsonSchema
from fastapi.responses import StreamingResponse
from src.logger import logger
import src.conv_history as ch
import src.intent_retriever as int_ret


# import logging
# # Uvicorn's default logger
# logger = logging.getLogger("uvicorn.error")
app=FastAPI(title=APP_CONFIG["app"]["name"])
#for multiple pdf files handling
CustomUploadFile = Annotated[UF, WithJsonSchema({"type": "string", "format": "binary"})]

@app.post("/ingest")
def ingest(files: list[CustomUploadFile]=File(...)):
    logger.info("Ingesting uploaded PDF or PDF's ............")
    tot_chunks=0
    try:
        for file in files:
            try:
                text=ing.load_pdf(file)
                logger.info("loading pdf completed ............")
            except Exception as e1:
                logger.exception(f"Error occurred during loading pdf : {e1}")
                
            try:
                chunks=ing.chunk_text(text)
                logger.info("text chunking completed ............")
            except Exception as e2:
                logger.exception(f"Error occurred during chunking : {e2}")
                
            try:
                ing.chroma_ingest(file,chunks)
            except Exception as e3:
                logger.exception(f"Error occurred during ingesting chromadb : {e3}")
            tot_chunks+=len(chunks)
        if tot_chunks:
            logger.info("Ingestion completed ............")
            return {
                "status":"Success",
                "files_processed":len(files),
                "total_chunks":tot_chunks,
                "error_description":""
            }
        else:
            return {
                "status":"Failure",
                "files_processed":len(files),
                "total_chunks":tot_chunks,
                "error_description":"Something went Wrong While ingesting Pdf's"
            }
    except Exception as e:
        logger.exception(f"Error occurred during Ingestion : {e}")
    
@app.get("/query")
async def infer(question:str,source:Optional[str]=Query(None)):
    print("This is print log printing in log file...........")
    logger.info("In inference............question==="+question)
    
    try:
        logger.info("In inference....before fetching history")
        history = ch.history_to_text()
        logger.info(f"In inference....after fetching history...{history}")

        intent=int_ret.isFollowUp(question,history)
        logger.info(f"In inference....after getting intent===={intent}")

        if intent=="YES":
            ret_context=history
        else:
            try:
                results=ret.retriever(question,source)
                ret_chunks = results["documents"][0]
            except Exception as e4:
                logger.exception(f"Error occurred during retrieval of query : {e4}")
                return {"answer": "An error occurred during retrieval."}
    
            if not ret_chunks:
                return {
                    "answer": "No relevant information found."
                }
            logger.info("In inference.... before reranking")
    
            try:
                ranked_res=rerank.rerank_docs(question,ret_chunks)
            except Exception as e5:
                logger.exception(f"Error occurred during reranking docs : {e5}")
            logger.info("In inference.... after reranking")
            logger.info("In inference.... before get context")
    
            try:
                ret_context=util.get_context(ranked_res)
            except Exception as e6:
                logger.exception(f"Error occurred during reranking docs : {e6}")
        
    
        logger.info("In inference.... after get context")
        logger.info(ret_context)
        #logger.info("In inference....before fetching history")
        #history = ch.history_to_text()
        logger.info("In inference....before streaming llm history...")

        return StreamingResponse(
            util.stream_llm_response(question, ret_context, history),
            #media_type="text/plain"
            media_type="text/event-stream"   
        )
    except Exception as ex:
        logger.exception(f"Error occurred in inference : {ex}")
    
    
    
    
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_config=None
    )