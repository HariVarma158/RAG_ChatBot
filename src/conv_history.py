from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from typing import TypedDict
from langchain_core.messages import HumanMessage, AIMessage
from src.logger import logger



# =====================================================
# LANGGRAPH MEMORY
# =====================================================
memory = MemorySaver()
THREAD_ID = "default"

class MemoryState(TypedDict):
    messages: list

def memory_node(state: MemoryState):
    return {"messages": state["messages"]}

builder = StateGraph(MemoryState)
builder.add_node("memory", memory_node)

builder.add_edge(START, "memory")
builder.add_edge("memory", END)

graph = builder.compile(checkpointer=memory)

# =====================================================
# MEMORY HELPERS
# =====================================================
def get_memory_messages():
    logger.info("In get_memory_messages")
    try:
        snapshot = graph.get_state(
            {
                "configurable": {
                    "thread_id": THREAD_ID
                }
            }
        )
        
        return snapshot.values.get("messages", [])

    except Exception as e:
        logger.exception(f"In get_memory_messages error...{e} ")
        return []


def update_memory(question: str, answer: str):
    try:
        logger.info("In update_memory..")
        messages = get_memory_messages()
        logger.info(f"In update_memory..after messages==={messages}")
        
        messages.append(
            HumanMessage(content=question)
        )
        messages.append(
            AIMessage(content=answer)
        )

        # Keep only last 10 messages
        messages = messages[-10:]
        logger.info(f"In update_memory..after final messages==={messages}")

        graph.invoke(
            {
                "messages": messages
            },
            {
                "configurable": {
                    "thread_id": THREAD_ID
                }
            }
        )
    except Exception as e:
        logger.exception(f"Exception In update_memory..{e}")



def history_to_text():
    try:
        logger.info("In history_to_text")
        messages = get_memory_messages()
        logger.info(f"In history_to_text after get memory messages...{messages}")

        if not messages:
            return "No previous conversation."

        formatted = []

        for msg in messages:
            if isinstance(msg, HumanMessage):
                formatted.append(
                    f"User: {msg.content}"
                )

            elif isinstance(msg, AIMessage):
                formatted.append(
                    f"Assistant: {msg.content}"
                )
        
        logger.info(f"In history_to_text after formatiing messages...{formatted}")
        return "\n".join(formatted)
    except Exception as e:
        logger.exception(f"Exception In history_to_text..{e}")
