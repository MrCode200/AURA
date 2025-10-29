import logging

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent
from langchain_ollama import ChatOllama

from src.agent.engines import AudioEngine
from config import settings
from tools import tool_registry

logger = logging.getLogger("aura.log")


class Agent:
    def __init__(self):
        self.audio_engine = AudioEngine()
        self.agent = self._create_agent()

    @staticmethod
    def _create_agent():
        llm = ChatOllama(
            model="qwen3:8b-q4_K_M", #TODO: get from settings
            temperature=0
        )

        checkpointer = InMemorySaver()
        tools = [tool for name, tool in tool_registry.registry.items()]
        print(tools)
        agent = create_react_agent(
            model=llm,
            tools=tools,
            prompt=settings.system_prompt, # TODO: get from settings
            debug=True,
            checkpointer=checkpointer,
        )
        return agent

    def start(self):
        logger.info("Agent AURA started.")
        while True:
            if self.audio_engine.listen_for_wake_word():
                logger.debug("Wake word detected!")
                self.audio_engine.play_audio(f"yes_master_{settings.tts_speaker}.wav")

                user_prompt: str = self.audio_engine.speech_to_text()['text']
                print(user_prompt) # TODO: logger.debug

                config = {"configurable": {"thread_id": "session1"}}
                response = self.agent.invoke({"messages": [{"role": "user", "content": user_prompt}]}, config)
                print(response["messages"][-1].content) # TODO: logger.debug
                self.audio_engine.text_to_speech(response["messages"][-1].content)