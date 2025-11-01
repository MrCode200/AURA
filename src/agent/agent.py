import logging

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent
from langchain_ollama import ChatOllama

from src.agent.engines import AudioEngine
from config import settings
from tools import tool_registry

logger = logging.getLogger("aura.log")


class Agent:
    def __init__(self, wait_for_audio_end: bool = True):
        self.audio_engine = AudioEngine(wait_for_audio_end)
        self.agent = self._create_agent()
        self.stop = False

    @staticmethod
    def _create_agent():
        llm = ChatOllama(
            model=settings.agent_model, #TODO: get from settings
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
        while not self.stop:
            if self.audio_engine.listen_for_wake_word():
                logger.debug("Wake word detected!")
                self.audio_engine.play_audio(f"yes_master_{settings.tts_speaker}.wav")

                user_prompt: str = self.audio_engine.speech_to_text()['text']
                print(user_prompt) # TODO: logger.debug

                config = {"configurable": {"thread_id": "session1"}}
                response = self.agent.invoke({"messages": [{"role": "user", "content": user_prompt}]}, config)
                print(response["messages"][-1].content) # TODO: logger.debug
                self.audio_engine.text_to_speech(response["messages"][-1].content)

        self.stop = False

    def stop(self):
        self.stop = True
        self.audio_engine.close()
