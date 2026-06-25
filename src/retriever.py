from src.config import chromaDb as chdb
from src.logger import logger
def retriever(question:str,source=str):
    logger.info("in retriever======")
    if source:
            where_filter = {"source": source}
    else:
        where_filter = None
    logger.info(where_filter)

    logger.info("Before Chroma query")

    results=chdb.collection.query(
        query_texts=[question],
        n_results=15,
        where=where_filter
    )
    logger.info("after Chroma query")

    logger.info(f"results type = {type(results)}")

    if results:
        logger.info(f"results keys = {list(results.keys())}")
        logger.info(
            f"retrieved chunks = {len(results['documents'][0])}"
        )
    return results