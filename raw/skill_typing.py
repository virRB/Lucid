import json
from openai.types.chat import ChatCompletionMessageToolCall
import inspect


class _Types:
    def __init__(self: _Types) -> None:
        self.S = {"type": "string"}

types = _Types()

def tool(name: str, desc: str, props: dict, required: list) -> dict:
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": desc,
            "parameters": {
                "type": "object",
                "properties": props,
                "required": required
            }
        }
    }

def execute(call: ChatCompletionMessageToolCall, SKILLS: dict, workspace: str|None=None, confirm: set[str]|None=None, access: bool=False) -> dict:
    name = call.function.name
    try:
        args = json.loads(call.function.arguments or "{}")
        if name not in SKILLS:
            return {"error": f"Error: unknown skill '{name}'. Available: {', '.join(SKILLS)}"}
        if confirm and name in confirm and not access:
            return {"status": "pending", "reason": "confirm"}
        skill = SKILLS[name]
        parameters = inspect.signature(skill).parameters
        if "workspace" in parameters:
            args["workspace"] = workspace
        result = skill(**args)
        return result if result is not None else {"status": "complete"}
    except json.JSONDecodeError:
        return {"error": "Error: arguments were not valid JSON."}
    except TypeError as e:
        return {"error": "Error: wrong arguments for '{name}': {e}"}
    except Exception as e:
        return {"error": e}
