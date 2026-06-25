from src.config import chromaDb as chdb
from src.logger import logger

def rerank_docs(question,ret_chunks):
    logger.info("In Rerank docs")
    #print(ret_chunks)
    logger.info(f"Retrieved {len(ret_chunks)} chunks")
    pairs=[(question,doc) for doc in ret_chunks]
    scores=chdb.reranker.predict(pairs)
    ranked_res=sorted(
        zip(scores,ret_chunks),
        key=lambda x:x[0],
        reverse=True
    )
    #print(ranked_res)
    return ranked_res