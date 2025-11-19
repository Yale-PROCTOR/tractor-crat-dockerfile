#!/usr/bin/env python3

import json
import sys

from pathlib import Path

if __name__ == "__main__":
    build_root = Path(sys.argv[1])
    source_root = Path(sys.argv[2])
    command_file_path = Path(sys.argv[3])

    cmake_reply_root = build_root / ".cmake" / "api" / "v1" / "reply"

    index_path = tuple(cmake_reply_root.glob("index-*.json"))[0]
    with open(index_path, "r") as f:
        index = json.load(f)

    codemodel_filename = index["reply"]["codemodel-v2"]["jsonFile"]
    codemodel_path = cmake_reply_root / codemodel_filename
    with open(codemodel_path, "r") as f:
        codemodel = json.load(f)

    targets = codemodel["configurations"][0]["targets"]

    dependencies: "dict[Path, list[Path]]" = {}
    executable: "Path | None" = None

    for target in targets:
        json_filename = target["jsonFile"]
        json_path = cmake_reply_root / json_filename
        sources_: "list[Path]" = []
        with open(json_path, "r") as f:
            target_data = json.load(f)

            if "link" in target_data:
                for fragment in target_data["link"]["commandFragments"]:
                    if fragment["role"] == "flags":
                        continue
                    if fragment["fragment"].startswith("-"):
                        continue
                    sources_.append(build_root / fragment["fragment"])

            if target_data["type"] == "OBJECT_LIBRARY":
                assert len(target_data["artifacts"]) == len(target_data["sources"])
                for artifact, source in zip(target_data["artifacts"], target_data["sources"]):
                    sources = sources_.copy()
                    sources.append(source_root / source["path"])
                    artifact_path = build_root / artifact["path"]
                    dependencies[artifact_path] = sources
            else:
                assert len(target_data["artifacts"]) == 1
                artifact = target_data["artifacts"][0]
                artifact_path = build_root / artifact["path"]
                if target_data["type"] == "EXECUTABLE":
                    assert executable is None
                    executable = artifact_path
                sources = sources_
                for source in target_data["sources"]:
                    sources.append(source_root / source["path"])
                dependencies[artifact_path] = sources

    assert executable is not None
    worklist = [executable]
    sources = set()

    while worklist:
        path = worklist.pop()
        if path.suffix == ".c":
            sources.add(path)
        else:
            deps = dependencies[path]
            worklist.extend(deps)

    with open(command_file_path, "r") as f:
        commands = json.load(f)
    
    filtered_commands = [cmd for cmd in commands if Path(cmd["file"]) in sources]

    with open(command_file_path, "w") as f:
        json.dump(filtered_commands, f, indent=2)
