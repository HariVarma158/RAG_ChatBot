import asyncio
from src.config import chromaDb as chdb
from src.logger import logger
import src.conv_history as ch
import src.orchestrator as orc
import src.utils as util

def get_context(ranked_res:list[tuple[float,str]]):
    #top n chunks
    top_chunks=[ doc for scores,doc in ranked_res[:chdb.top_n_context]]
    ret_Context="\n\n".join(top_chunks)
    # print(ret_Context)
    return ret_Context

async def stream_llm_response(question:str,ret_context:str,history:str):
    logger.info("in stream llm response")
    try:
        prompt=chdb.prompt_template.format(
            context=ret_context,
            question=question,
            history=history
        )
        #logger.info("prompt")

        #logger.info(f"prompt=={prompt}")
        """
        full_ans=chdb.llm.invoke(prompt)
        # async for chunk in chdb.llm.astream(prompt):
        #     if chunk.content:
        #         full_answer += chunk.content
        #         yield chunk.content
        #         await asyncio.sleep(0.001)
        logger.info(f"final answer=== {full_ans}")

        ch.update_memory(question, full_ans.content)
        return full_ans.content
        """
        async for chunk in chdb.llm.astream(prompt):

            if chunk.content:
                #full_answer += chunk.content

                # Send this chunk immediately
                yield chunk.content

                await asyncio.sleep(0.001)

        #logger.info(f"Final answer = {full_answer}")

        #ch.update_memory(question, full_answer)

        
    except Exception as e:
        logger.exception(f"Error while Streaming response....{e}")
        yield f"Error while Streaming response"
        
