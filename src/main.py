from logging import DEBUG
from pathlib import Path

from dotenv import load_dotenv
from magic_utils import setup_logger


def main():
    print(str(Path(".").resolve().parent))
    logger = setup_logger(
        "aura.log",
        str(Path(".").resolve().parent.joinpath("logs/log.jsonl")),
        DEBUG,
        DEBUG,
    )
    logger.info("Starting AURA...")
    load_dotenv()

    from src.agent import Agent # First create logger, then import other modules
    agent = Agent()
    agent.start()


if __name__ == '__main__':
    main()
