from nicegui import ui
import os
import asyncio
import json
import shutil
import tkinter
from tkinter import filedialog
from openai.types.chat import ChatCompletionMessageToolCall
import main as model
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = HERE
HOST = "127.0.0.1"
PORT = 8000
URL = f"http://{HOST}:{PORT}"

CHATS = os.path.join(BASE, "chats")
MEMORY = os.path.join(HERE, "memory.json")
ATTATCHMENTS = os.path.join(HERE, "attatchments")

with open(os.path.join(HERE, "style.css"), "r", encoding="utf-8") as f:
    ui.add_css(f.read())

frames: list[ui.element] = []

async def confirm(call: ChatCompletionMessageToolCall) -> bool:
    name = call.function.name
    args = json.loads(call.function.arguments or "{}")
    def format_args(args: dict) -> str:
        result = []
        for key, val in args.items():
            result.append(f"{key}: {val}")
        return "\n".join(result)
    ans = await choice(f"Lucid wants to use the '{name}' tool\n{format_args(args)}", "Yes", "No")
    return bool(ans == "Yes")

def Frame() -> ui.element:
    frame = ui.element("div").classes("app")
    frames.append(frame)
    return frame

def show_frame(frame: ui.element) -> None:
    for f in frames:
        f.set_visibility(False)
    frame.set_visibility(True)

def add_back_buttons() -> None:
    for frame in frames:
        if frame == HomeFrame:
            continue
        def back() -> None:
            show_frame(HomeFrame)
            clear_frames()
        with frame:
            BackButton = ui.button(text="🏠", on_click=back)
            BackButton.classes("quick-button")
            BackButton.style("position: absolute; top: 25px; left: 25px; z-index: 1000;")


def clear_frames() -> None:
    for frame in frames:
        for child in list(frame.default_slot.children):
            child.delete()
        if hasattr(frame, "build"):
            frame.build()
    add_back_buttons()

def alert(*message: str) -> None:
    message = "\n".join(message)
    with ui.dialog().props("persistent") as dialog:
        with ui.card():
            ui.label(message).classes("l-label")
            ui.button(text="OK", on_click=dialog.close)
    dialog.open()

async def prompt(*question: str) -> str|None:
    q = "\n".join(question)
    complete = asyncio.Event()
    result: str|None = None
    with ui.dialog().props("persistent") as dialog:
        with ui.card().style("position: relative; width: 200px; padding-top: 65px;"):
            ui.label(q).classes("l-label")
            PromptBox = ui.input(placeholder="Enter text...")
            PromptBox.classes("message-box")
            def send() -> None:
                nonlocal result
                value = PromptBox.value.strip()
                if not value:
                    alert("Please write something in the box!")
                    return
                result = value
                dialog.close()
                complete.set()
            def cancel() -> None:
                nonlocal result
                result = None
                dialog.close()
                complete.set()
            ui.button(text="Send", on_click=send)
            CloseButton = ui.button(text="X", on_click=cancel)
            CloseButton.classes("quick-button")
            CloseButton.style("position: absolute; top: 10px; right: 10px; background-color: red !important;")
    dialog.open()
    await complete.wait()
    return result

async def choice(message: str, *choices: str, close: bool=True) -> str|None:
    result: str|None = None
    completed = asyncio.Event()
    with ui.dialog().props("persistent") as dialog:
        with ui.card().style("position: relative; width: 200px; padding-top: 65px;"):
            ui.label(message).classes("l-label")
            for _choice in choices:
                def _set(val: str) -> None:
                    nonlocal result
                    dialog.close()
                    result = val
                    completed.set()
                ui.button(text=_choice, on_click=lambda c=_choice: _set(c))
            def cancel() -> None:
                nonlocal result
                result = None
                dialog.close()
                completed.set()
            if close:
                CancelButton = ui.button(text="X", on_click=cancel)
                CancelButton.classes("quick-button")
                CancelButton.style("position: absolute; top: 10px; right: 10px; background-color: red !important;")
    dialog.open()
    await completed.wait()
    return result

HomeFrame = Frame()
ChatFrame = Frame()
SettingsFrame = Frame()
SumMemFrame = Frame()

def ask_dir(file: bool=False) -> str|None:
    root = tkinter.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    if not file:
        _dir = filedialog.askdirectory(parent=root)
    else:
        _dir = filedialog.askopenfilename()
    root.destroy()
    return _dir or None

async def create_chat() -> None:
    name = await prompt("The Chat wants a name...")
    if name is None:
        return
    BARRED = '<>:"/\\|?*'
    BARRED_NAMES = ["CON", "PRN", "AUX", "NUL", *[f"COM{i}" for i in range(1, 10)], *[f"LPT{i}" for i in range(1, 10)], ".", ".."]
    for char in BARRED:
        if char in name:
            alert(f"Names cannot use character '{char}'!")
            return
    if name.upper() in BARRED_NAMES:
        alert(f"{name} cannot be used!")
        return
    if name.endswith((" ", ".")):
        alert("Names cannot end with ' ' or '.'!")
        return
    config_ws = await choice("📁 Where should Lucid work?\nThis is where it can modify, read and write files in\nFiles can also be provided as attatchments (Read Only)", "Select Folder", "Skip")
    if config_ws is None:
        return
    if config_ws == "Select Folder":
        workspace = ask_dir()
    elif config_ws == "Skip":
        workspace = None
    filename = f"{name}.json"
    filepath = os.path.join(CHATS, filename)
    if os.path.exists(filepath):
        alert(f"{name} already exists!")
        return
    chat_type = await choice("Chat persistence type", "Save", "Temporary")
    if chat_type is None:
        return
    chat_struct = {
        "name": name,
        "temp": True if chat_type == "Temporary" else False,
        "messages": [],
        "workspace": workspace
    }
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(json.dumps(chat_struct, indent=4))
    await show_chat(filepath)
    
    
async def show_chat(path: str) -> None:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data: dict = json.loads(f.read())
    except Exception:
        alert("Failed to load chat...")
        return
    temp: bool = data["temp"]
    messages: list[dict] = data["messages"]
    workspace: str | None = data["workspace"]
    clear_frames()
    with ChatFrame:
        if workspace is not None:
            workspace_display = f"🛠️ Workspace: {workspace}"
        else:
            workspace_display = "🔒 No workspace selected!"
        Display = ui.label(text=workspace_display)
        Display.style("position: absolute; top: 2vh; left: 30vw; color: black; z-index: 999;")

        def add_attatchment() -> None:
            file = ask_dir(file=True)
            if file is None:
                return
            filename = os.path.basename(file)
            new = os.path.join(ATTATCHMENTS, filename)
            if os.path.exists(new):
                alert(f"{filename} has already been given as an attatchment!")
                return
            shutil.copy(file, new)
            alert(f"Added attatchment {filename}!")
            
        Attatchment = ui.button(text="+", on_click=add_attatchment)
        Attatchment.classes("quick-button")
        Attatchment.style("position: absolute; top: 85px; left: 25px; z-index: 999;")
    show_frame(ChatFrame)
    def format_tool_calls(tool_calls: list[dict]) -> str:
        output = []
        for call in tool_calls:
            function = call["function"]
            tool_name = function["name"]
            arguments = json.loads(function["arguments"])
            output.append(f"Used Tool: {tool_name}")
            for key, value in arguments.items():
                output.append(f"{key}: {value}")
        return "\n".join(output)
    async def display_message(message: str|dict, user: bool = True) -> None:
        if not message:
            return
        with MessagesFrame:
            Message = ui.element("div")
            if user:
                Message.classes("user-prompt")
                Message.style("align-self: flex-start;")
            else:
                Message.classes("model-response")
                Message.style("align-self: flex-end;")
            with Message:
                if isinstance(message, dict):
                    content = message.get("content")
                    if content:
                        ui.label(text=content).classes("l-label")
                else:
                    ui.label(text=message).classes("l-label")
        await asyncio.sleep(0)
    async def send(message: str) -> None:
        nonlocal messages
        message = message.strip()
        if not message:
            return
        PromptBox.value = ""
        SendButton.disable()
        try:
            await display_message(message, user=True)
            events = await model.ask(message, workspace=workspace, temp=temp, mem=messages, confirm=confirm)
            for event in events:
                if event["role"] != "assistant":
                    continue
                tool_calls = event.get("tool_calls", [])
                if tool_calls:
                    await display_message(format_tool_calls(tool_calls), user=False)
                content = event.get("content")
                if content:
                    await display_message(content, user=False)
            if not temp:
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(data|{"messages": messages}, f, indent=4, ensure_ascii=False)
        except Exception as e:
            alert(f"An error occurred:\n{e}")
        finally:
            SendButton.enable()
    with ChatFrame:
        with ui.element("div").style("position: absolute; inset: 0; display: flex; justify-content: center; align-items: center;"):
            PromptBox = ui.input(placeholder="Ask anything...")
            PromptBox.style("position: absolute; width: 85vw; top: 80vh;")
            PromptBox.classes("message-box")
            SendButton = ui.button(text="➡️", on_click=lambda: send(PromptBox.value))
            SendButton.classes("quick-button")
            SendButton.style("position: absolute; top: 81vh; left: 93vw;")
            MessagesFrame = ui.element("div")
            MessagesFrame.classes("scrollable-container")
            MessagesFrame.style("position: fixed; left: 10vw; width: 80vw; top: 10vh; height: 65vh; display: flex;")
            for message in messages:
                if message["role"] == "user":
                    await display_message(message["content"], user=True)
                elif message["role"] == "assistant":
                    tool_calls = message.get("tool_calls", [])
                    if tool_calls:
                        await display_message(format_tool_calls(tool_calls), user=False)
                    if message.get("content"):
                        await display_message(message["content"], user=False)


def buildHomeFrame() -> None:
    with HomeFrame:
        SettingsButton = ui.button(text="⚙️", on_click=lambda: show_frame(SettingsFrame))
        SettingsButton.style("position: absolute; top: 7vh; left: 7vw;")
        SettingsButton.classes("quick-button")

        CreateChatButton = ui.button(text="New Chat", on_click=create_chat)
        CreateChatButton.style("position: absolute; top: 25vh; left: 7vw;")
        CreateChatButton.classes("fancy-button")

        async def open_chat() -> None:
            if len(os.listdir(CHATS)) == 0:
                create = await choice("No chats available... Create one?", "Yes", "No", close=False)
                if create == "Yes":
                    await create_chat()
                    return
                else:
                    return
            for path in [os.path.join(CHATS, p) for p in os.listdir(CHATS)]:
                if os.path.isdir(path):
                    confirm = await choice(f"Found unexpected folder (\"{os.path.basename(path)}\")... Delete?", "Hell Yes", "No Thanks", close=False)
                    if confirm == "Hell Yes":
                        shutil.rmtree(path)
                    else:
                        continue
                    continue
                if not path.lower().endswith(".json"):
                    os.remove(path)
                    continue
            chat = await choice("Open a chat", *[p.removesuffix(".json") for p in os.listdir(CHATS)])
            if chat is None:
                return
            chat = os.path.join(CHATS, f"{chat}.json")
            await show_chat(chat)

        async def delete_chat() -> None:
            if len(os.listdir(CHATS)) == 0:
                create = await choice("No chats available... Create one?", "Yes", "No", close=False)
                if create == "Yes":
                    await create_chat()
                    return
                else:
                    return
            for path in [os.path.join(CHATS, p) for p in os.listdir(CHATS)]:
                if os.path.isdir(path):
                    confirm = await choice(f"Found unexpected folder (\"{os.path.basename(path)}\")... Delete?", "Hell Yes", "No Thanks", close=False)
                    if confirm == "Hell Yes":
                        shutil.rmtree(path)
                    else:
                        continue
                    continue
                if not path.lower().endswith(".json"):
                    os.remove(path)
                    continue
            chatname = await choice("Delete a chat", *[p.removesuffix(".json") for p in os.listdir(CHATS)])
            if chatname is None:
                return
            chat = os.path.join(CHATS, f"{chatname}.json")
            confirm = await choice(f"Delete {chatname}?", "Yes", "No")
            if confirm == "No":
                return
            os.remove(chat)

        OpenChat = ui.button(text="Open Chat", on_click=open_chat)
        OpenChat.style("position: absolute; top: 50vh; left: 7vw;")
        OpenChat.classes("fancy-button")

        DeleteChat = ui.button(text="Delete Chat", on_click=delete_chat)
        DeleteChat.style("position: absolute; top: 75vh; left: 7vw;")
        DeleteChat.classes("fancy-button")

def buildSettingsFrame() -> None:
    async def sum_memory() -> None:
        with open(MEMORY, "r", encoding="utf-8") as f:
            memory = json.loads(f.read())
        clear_frames()
        show_frame(SumMemFrame)
        with SumMemFrame:
            BackButton = ui.button(text="⬅️", on_click=lambda: show_frame(SettingsFrame))
            BackButton.classes("quick-button")
            BackButton.style("position: absolute; top: 10vh; left: 10vw;")

            Text = ui.label("Generating memory...")
            Text.style("position: relative; top: 30vh;")
            ui.update()
            response = await model.ask("Create a summary of this user - do not use any tools - only use the information provided", confirm=confirm, mem=memory, temp=True)
            try:
                Text.set_text(response[-1].get("content"))
            except Exception:
                Text.set_text("Invalid memory found...")
            Text.classes("l-label")

    async def manage_attatch() -> None:
        contents = os.listdir(ATTATCHMENTS)
        if len(contents) == 0:
            alert("Nothing to delete!")
            return
        victim = await choice("What would you like to delete?", *contents)
        if victim is None:
            return
        victim = os.path.join(ATTATCHMENTS, victim)
        os.remove(victim)
        alert(f"Deleted {os.path.basename(victim)}!")
    with SettingsFrame:
        Summary = ui.button(text="Memory Summary", on_click=sum_memory)
        Summary.classes("fancy-button")
        Summary.style("position: absolute; top: 15vh; left: 10vw;")

        ManageAttatch = ui.button(text="Manage Attatchments", on_click=manage_attatch)
        ManageAttatch.classes("fancy-button")
        ManageAttatch.style("position: absolute; top: 35vh; left: 10vw;")

HomeFrame.build = buildHomeFrame
SettingsFrame.build = buildSettingsFrame

clear_frames()
show_frame(HomeFrame)


ui.run(native=True, host=HOST, port=PORT, reload=False)