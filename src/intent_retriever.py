from src.config import chromaDb as chdb 
from src.logger import logger

def isFollowUp(question,history):
    logger.info("in is Follow up method")
    prompt=chdb.intent_prompt.format(
            question=question,
            history=history
        )
    result= chdb.llm.invoke(prompt)
    logger.info(f"result======{result}")

    return result.content.strip()