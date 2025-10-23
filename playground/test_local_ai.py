from typing import Annotated, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field
from langchain_ollama.llms import OllamaLLM
from typing_extensions import TypedDict

from test_tools import tools

agent = OllamaLLM(model="phi3:mini")

class State(TypedDict):
    messages: Annotated[list, add_messages]

def chatbot(state: State):
    return {"messages": [agent.invoke(state["messages"])]}

graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

graph = graph_builder.compile()

user_input = input("Enter a message: ")
state = graph.invoke({"messages": [{"role": "user", "content": user_input}]})

print(state["messages"][-1].content)