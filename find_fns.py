#!/usr/bin/env python3
import sys
import toml
import json
from pathlib import Path
from clang.cindex import Index, CursorKind


def preserve_option(option: str) -> bool:
    return (
        option.startswith("-D")
        or option.startswith("-I")
        or option.startswith("-std=")
        or option.startswith("-m")
    )


def visit(node, names: "set[str]", source_root: Path):
    if node.kind == CursorKind.FUNCTION_DECL and node.location.file is not None:
        decl_file = Path(node.location.file.name)
        if decl_file.is_relative_to(source_root) and decl_file.suffix == ".h":
            names.add(node.spelling)

    for child in node.get_children():
        visit(child, names, source_root)


if __name__ == "__main__":
    commands_file = Path(sys.argv[1])
    source_root = Path(sys.argv[2]).resolve()
    out_file = Path(sys.argv[3])

    with open(commands_file, "r") as f:
        commands = json.load(f)

    names = set()

    for command in commands:
        args = [opt for opt in command["command"].split() if preserve_option(opt)]
        index = Index.create()
        tu = index.parse(command["file"], args=args)
        visit(tu.cursor, names, source_root)

    config_toml = toml.loads("")
    config_toml["c_exposed_fns"] = sorted(names)
    with open(out_file, "w") as file:
        toml.dump(config_toml, file)
