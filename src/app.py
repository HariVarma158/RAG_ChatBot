from fastapi import FastAPI, File, UploadFile as UF, Query
from typing import Annotated,Optional
from src.config_loader import APP_CONFIG
import src.ingest as ing
from pydantic import WithJsonSchema
from fastapi.responses import StreamingResponse
from src.logger import logger
import src.orchestrator as orc

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
        return StreamingResponse(
            orc.process_request(question,source),
            media_type="text/event-stream"
        )
    except Exception as e:
        logger.exception(f"Error occurred in inference : {e}")
    
    
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_config=None
    )