import skill_typing
import skill


types = skill_typing._Types()

TOOLS = [
    skill_typing.tool(
        "readfile",
        "Read a file from a given filename",
        {"filename": skill_typing.types.S},
        ["filename"]
    ),
    skill_typing.tool(
        "makefile",
        "Create a file from a given filename",
        {"filename": skill_typing.types.S},
        ["filename"]
    ),
    skill_typing.tool(
        "writefile",
        "Write content to an existing file",
        {"filename": skill_typing.types.S, "content": skill_typing.types.S},
        ["filename", "content"]
    ),
    skill_typing.tool(
        "searchweb",
        "Search something on the internet",
        {"query": skill_typing.types.S},
        ["query"]
    ),
    skill_typing.tool(
        "readattatchment",
        "Read an attatchment provided by the user",
        {"filename": skill_typing.types.S},
        ["filename"]
    ),
    skill_typing.tool(
        "runcommand",
        "Run a command in the given workspace (and get its return value)",
        {"command": skill_typing.types.S},
        ["command"]
    )
]

SKILLS = {
    "readfile": skill.readfile,
    "makefile": skill.makefile,
    "writefile": skill.writefile,
    "searchweb": skill.searchweb,
    "readattatchment": skill.readattatchment,
    "runcommand": skill.runcommand
}

NEEDS_CONFIRM = [
    "writefile",
    "makefile",
    "runcommand"
]