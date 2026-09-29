from openai import AsyncOpenAI
import os
import json
import skills
import skill_typing

HERE = os.path.dirname(os.path.abspath(__file__))
MEMORY = os.path.join(HERE, "memory.json")
SYSTEM = os.path.join(HERE, "system.md")

with open(MEMORY, "r", encoding="utf-8") as f:
    memory: list = json.loads(f.read())

model = "qwen2.5-1.5b-instruct"

client = AsyncOpenAI(base_url="http://localhost:1234/v1", api_key="space-monkeys-declined-your-offer-for-an-api-key")


async def ask(prompt: str, confirm, mem: list|None=None, max_steps: int=5, workspace: str|None=None, temp: bool=False) -> list:
    if mem is None:
        mem = memory
    start = len(mem)
    mem.append({"role": "user", "content": prompt})
    for _ in range(max_steps):
        completion = await client.chat.completions.create(model=model, messages=mem, temperature=0.2, tools=skills.TOOLS)
        msg = completion.choices[0].message
        mem.append(msg.model_dump(exclude_none=True))
        if not msg.tool_calls:
            break
        for call in msg.tool_calls:
            e = skill_typing.execute(call, skills.SKILLS, workspace=workspace, confirm=skills.NEEDS_CONFIRM)
            if e["status"] == "pending":
                if e["reason"] == "confirm":
                    ans = await confirm(call)
                    if not ans:
                        e = {"status": "failed", "reason": "User declined permission"}
                        break
                    else:
                        e = skill_typing.execute(call, skills.SKILLS, workspace=workspace, access=True, confirm=skills.NEEDS_CONFIRM)
            mem.append({"role": "tool", "tool_call_id": call.id, "content": json.dumps(e)})
    else:
        mem.append({"role": "assistant", "content": "Stopped: too many tool steps."})
    if not temp:
        with open(MEMORY, "w", encoding="utf-8") as f:
            f.write(json.dumps(mem, indent=4, ensure_ascii=False))
    return mem[start:]


if not memory:
    with open(SYSTEM, "r", encoding="utf-8") as f:
        instructions = f.read()
    with open(MEMORY, "w", encoding="utf-8") as f:
        f.write(json.dumps([{"role": "system", "content": instructions}], indent=4, ensure_ascii=False))