from logging import DEBUG
from pathlib import Path

from dotenv import load_dotenv
from magic_utils import setup_logger

from config import settings

def main():
    print(str(Path(".").resolve().parent))
    logger = setup_logger(
        "aura.log",
        str(settings.root_path.joinpath("logs/log.jsonl")),
        DEBUG,
        DEBUG,
    )
    logger.info("Starting Project AURA...")
    load_dotenv()

    from src.agent import Agent # First create logger, then import other modules
    agent = Agent() #memory_saver=InMemorySaver()
    agent.start()


if __name__ == '__main__':
    main()
