from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent


from test_tools import tools

llm = ChatOllama(
    model="phi3:mini",
    validate_model_on_init=True,
    temperature=0
)

checkpointer = InMemorySaver()
agent = create_react_agent(
    model=llm,
    tools=tools,
    prompt="You are a helpful assistant. You always end your sentences with 'uwu'",
    checkpointer=checkpointer,
)

config = {"configurable": {"thread_id": "session1"}}
res1 = agent.invoke({"messages": [{"role": "user", "content": "Remeber the number 2"}]}, config)
res2 = agent.invoke({"messages": [{"role": "user", "content": "What number should you remember?"}]}, config)