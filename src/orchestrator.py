import src.retriever as ret
import src.reranker as rerank
import src.utils as util
from src.logger import logger
import src.conv_history as ch
import src.intent_retriever as int_ret
import json
import asyncio

async def process_request(question,source):
    
    logger.info("In inference....before fetching history")
    #yield here for getting history
    yield f"Fetching conversation history ..... \n"
    await asyncio.sleep(0.03)
    
    history = ch.history_to_text()
    logger.info(f"In inference....after fetching history...{history}")
    
    #yield here for follow up
    yield f"detecting Intent... \n"
    await asyncio.sleep(0.03)
    
    intent=int_ret.isFollowUp(question,history)
    logger.info(f"In inference....after getting intent===={intent}")

    if intent=="YES":
        ret_context=history
    else:
        try:
            #yield json.dumps({"status": "Searching"}) + "\n"
            yield f"Retrieving context... \n"
            await asyncio.sleep(0.03)
            
            results=ret.retriever(question,source)
            ret_chunks = results["documents"][0]
        except Exception as e4:
            logger.exception(f"Error occurred during retrieval of query : {e4}")
            yield f"No relevant information found \n"
            await asyncio.sleep(0.03)
            return
    
        if not ret_chunks:
            yield f"No relevant information found \n"
            await asyncio.sleep(0.03)
            return
        logger.info("In inference.... before reranking")
    
        try:
            yield f"Reranking context... \n"
            await asyncio.sleep(0.03)
            ranked_res=rerank.rerank_docs(question,ret_chunks)
        except Exception as e5:
            logger.exception(f"Error occurred during reranking docs : {e5}")
        logger.info("In inference.... after reranking")
        logger.info("In inference.... before get context")
    
        try:
            yield f"fetching context.... \n"
            await asyncio.sleep(0.03)
            
            ret_context=util.get_context(ranked_res)
        except Exception as e6:
            logger.exception(f"Error occurred during reranking docs : {e6}")
        
    
    logger.info("In inference.... after get context")
    logger.info(ret_context)
   
    full_answer=""
    async for chunk in util.stream_llm_response(question, ret_context, history):
        full_answer+=chunk
        yield chunk
    logger.info("In inference.... after sending llm streaming response and before updating memory")
    ch.update_memory(question, full_answer)
    
    #yield f"{llm_ans.content}"
