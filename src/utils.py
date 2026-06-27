import asyncio
from src.config import chromaDb as chdb
from src.logger import logger

def get_context(ranked_res:list[tuple[float,str]]):
    #top n chunks
    top_chunks=[ doc for scores,doc in ranked_res[:chdb.top_n_context]]
    ret_Context="\n\n".join(top_chunks)
    return ret_Context

async def stream_llm_response(question:str,ret_context:str,history:str):
    logger.info("in stream llm response")
    try:
        prompt=chdb.prompt_template.format(
            context=ret_context,
            question=question,
            history=history
        )

        async for chunk in chdb.llm.astream(prompt):
            if chunk.content:
                yield chunk.content
                await asyncio.sleep(0.001)
        
    except Exception as e:
        logger.exception(f"Error while Streaming response....{e}")
        yield f"Error while Streaming response"
        
