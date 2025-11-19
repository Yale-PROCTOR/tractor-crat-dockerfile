#!/usr/bin/env python3

import json
import sys

from pathlib import Path

if __name__ == "__main__":
    build_root = Path(sys.argv[1])
    cmake_reply_root = build_root / ".cmake" / "api" / "v1" / "reply"

    index_path = tuple(cmake_reply_root.glob("index-*.json"))[0]
    with open(index_path, "r") as f:
        index = json.load(f)

    codemodel_filename = index["reply"]["codemodel-v2"]["jsonFile"]
    codemodel_path = cmake_reply_root / codemodel_filename
    with open(codemodel_path, "r") as f:
        codemodel = json.load(f)

    targets = codemodel["configurations"][0]["targets"]
    libs = set()
    for target in targets:
        target_filename = target["jsonFile"]
        target_path = cmake_reply_root / target_filename
        with open(target_path, "r") as f:
            target = json.load(f)

        if "link" in target:
            for frag in target["link"]["commandFragments"]:
                if frag["role"] == "libraries":
                    fragment = frag["fragment"]
                    if fragment.startswith("-l"):
                        libs.add(fragment)

    with open(sys.argv[2], "r", encoding="utf-8") as f:
        lines = f.readlines()

    for lib in libs:
        lines.insert(4, f'    println!("cargo:rustc-link-arg={lib}");\n')

    with open(sys.argv[2], "w", encoding="utf-8") as f:
        f.writelines(lines)
