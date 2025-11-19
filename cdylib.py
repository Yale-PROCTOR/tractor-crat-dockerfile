#!/usr/bin/env python3

import sys
import toml
from pathlib import Path

if __name__ == "__main__":
    """
    This script is used to change the build process to generate a shared library
    rather than a static one. It replaces the current `crate-type` in Cargo.toml to be `cdylib`.

    Arguments: 
       * Path to the Rust project to convert to a shared library
    """
    cargo_toml_path = Path(sys.argv[1]).joinpath("Cargo.toml")

    with open(cargo_toml_path, "r") as f:
        cargo_toml = toml.load(f)

    cargo_toml["lib"]["crate-type"] = ["cdylib"]

    with open(cargo_toml_path, "w") as f:
        toml.dump(cargo_toml, f)
