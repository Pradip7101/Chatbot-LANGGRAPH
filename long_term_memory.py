import operator
from dotenv import load_dotenv

from typing_extensions import TypedDict, Annotated

from langgraph.graph import StateGraph, START, END

# from langgraph.checkpoint.memory import InMemorySaver

from langgraph.checkpoint.mongodb import MongoDBSaver


from langchain_groq import ChatGroq

load_dotenv()

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0
)
from langchain_core.messages import (
    AnyMessage,
    HumanMessage,
    SystemMessage,
    AIMessage,
)

class MessagesState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    llm_calls: int

def chatbot_node(state: MessagesState):
     print("🤖 Agent is responding...")
     response = llm.invoke(
            [
                SystemMessage(
                    content=(
                        "You are a helpful AI assistant. "
                        "Use conversation memory properly "
                        "and answer based on previous messages."
                    )
                )
            ]
            + state["messages"]
        )

     return {
        "messages": [response],
        "llm_calls": state.get("llm_calls", 0) + 1
    }



builder = StateGraph(MessagesState)

builder.add_node("chatbot", chatbot_node)

builder.add_edge(START, "chatbot")
builder.add_edge("chatbot", END)

# Memory server to store 



# with MongoDBSaver.from_conn_string("mongodb://localhost:27017","chatbot") as memory:
#     app = builder.compile(checkpointer=memory)

localhost="mongodb://localhost:27017"
mongo_db="chatbot"


config ={
    "configurable":{
        "thread_id":"user_1",
    }
}

with MongoDBSaver.from_conn_string(localhost,mongo_db) as memory:
   
    app = builder.compile(checkpointer=memory)

    result = app.invoke(
        {
            "messages": [
                HumanMessage(content="what is my name?"),
            ],
            "llm_calls": 0
        },
        config=config
    )

    print("\nAI Response 1:")
    print(result["messages"][-1].content)