import importlib
import pkgutil
import os

from magic_utils.registryManager import Registry

import logging

logger = logging.getLogger("aura.log")


tool_registry = Registry(
    registry_name="tool_registry",
    logger=logger
)

tools_dir = os.path.dirname(os.path.abspath(__file__))
logger.info("Loading tools...")
for finder, name, ispkg in pkgutil.iter_modules([tools_dir]):
    if name == "__init__":
        continue
    try:
        importlib.import_module(f"tools.{name}")
    except Exception as e:
        logger.error(f"Error loading tool {name}: {str(e)}")

logger.info("Finished Loading tools")