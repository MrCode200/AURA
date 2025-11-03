from subprocess import run, CalledProcessError

from tools import tool_registry
from tools.toolResponse import ToolResponse


@tool_registry.register_function()
def run_command(commands: str | list[str], new_terminal: bool = False):
    """
    Execute a shell command on the user's Windows system with user approval.

    This tool allows you to run terminal/command-line commands. The user will be prompted
    for approval before execution. Use this for tasks like:
    - Running scripts or programs
    - File operations (copy, move, delete, etc.)
    - System commands
    - Installing packages or dependencies
    - Git operations

    :param commands: The command to run. Example: ["python", "script.py"] or "python script.py"
    :param new_terminal: Whether to run the command in a new terminal or the one with the previous state

    Important:
        - If you don't have the precise location for your commands, use other commands to find and get a sense of the location
        - The command runs in a shell environment (shell=True)
        - Check the returned status to determine if the command succeeded
        - For names with spaces use "" example: mkdir "Hello World"

    :return: The stdout of the command
    """
    if isinstance(commands, str):
        commands = [commands]
    commands = (["start", "cmd", "/k"] + commands) if new_terminal else commands

    if input(f"Agent wants to run: {commands} (y/n)") != 'y':
        return ToolResponse(
            status="cancelled",
            message=f"User disallowed command",
            details={"args": commands}
        ).model_dump()


    try:
        data = run(commands, capture_output=True, shell=True, text=True, check=True)
        return ToolResponse(
            status="success",
            details={
                "args": commands,
                "stdout": data.stdout
            }
        ).model_dump()

    except CalledProcessError as e:
        return ToolResponse(
            status="error",
            details={
                "args": commands,
                "stdout": e.stdout,
                "stderr": e.stderr
            },
            error=str(e)
        ).model_dump()

    except Exception as e:
        return ToolResponse(
            status="error",
            details={
                "args": commands,
            },
            error=str(e)
        ).model_dump()
