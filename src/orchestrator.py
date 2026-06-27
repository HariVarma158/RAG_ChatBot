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
    #yield json.dumps({"status": "Searching"}) + "\n"
    await asyncio.sleep(0.05)
    
    history = ch.history_to_text()
    logger.info(f"In inference....after fetching history...{history}")
    
    #yield here for follow up
    yield f"detecting Intent... \n"
    #yield json.dumps({"status": "Searching"}) + "\n"
    await asyncio.sleep(0.05)
    
    intent=int_ret.isFollowUp(question,history)
    logger.info(f"In inference....after getting intent===={intent}")

    if intent=="YES":
        ret_context=history
    else:
        try:
            #yield json.dumps({"status": "Searching"}) + "\n"
            yield f"Retrieving context... \n"
            await asyncio.sleep(0.05)
            
            results=ret.retriever(question,source)
            ret_chunks = results["documents"][0]
        except Exception as e4:
            logger.exception(f"Error occurred during retrieval of query : {e4}")
            #return {"answer": "An error occurred during retrieval."}
            yield f"No relevant information found \n"
            #yield json.dumps({"status": "Searching"}) + "\n"
            await asyncio.sleep(0.1)
            return
    
        if not ret_chunks:
            # return {
            #         "answer": "No relevant information found."
            # }
            yield f"No relevant information found \n"
            await asyncio.sleep(0.05)
            #yield json.dumps({"status": "Searching"}) + "\n"
            return
        logger.info("In inference.... before reranking")
    
        try:
            yield f"Reranking context... \n"
            #yield json.dumps({"status": "Searching"}) + "\n"
            await asyncio.sleep(0.05)
            ranked_res=rerank.rerank_docs(question,ret_chunks)
        except Exception as e5:
            logger.exception(f"Error occurred during reranking docs : {e5}")
        logger.info("In inference.... after reranking")
        logger.info("In inference.... before get context")
    
        try:
            yield f"fetching context.... \n"
            #yield json.dumps({"status": "Searching"}) + "\n"
            await asyncio.sleep(0.05)
            
            ret_context=util.get_context(ranked_res)
        except Exception as e6:
            logger.exception(f"Error occurred during reranking docs : {e6}")
        
    
    logger.info("In inference.... after get context")
    logger.info(ret_context)
    #logger.info("In inference....before fetching history")
    #history = ch.history_to_text()
    #logger.info(f"In inference....before streaming llm history...{history}")
    #return ret_context, history
    #llm_ans=util.stream_llm_response(question,ret_context,history)
    #current = ""
    
    async for chunk in util.stream_llm_response(question, ret_context, history):
        yield chunk

   
    # for c in llm_ans:
    #     current += c
    #     # Send the progressively longer text
    #     yield f"{current}"

    #     await asyncio.sleep(0.01)
    
    #yield f"{llm_ans.content}"
    #yield json.dumps({"response": llm_ans.content}) + "\n"
