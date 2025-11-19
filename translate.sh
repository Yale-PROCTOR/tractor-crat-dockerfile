#!/bin/bash

set -euo pipefail

if [ $# -ne 1 ]; then
    exit 1
fi

rm -rf "$1/src" "$1/dst" "$1/build-ninja" "$1/translated_rust"
tmpdir=$(mktemp -d)
mkdir $tmpdir/src
cp -rL "$1" $tmpdir/src
mv $tmpdir/src "$1"
rmdir $tmpdir
name=$(basename "$1")
src=$(realpath "$1/src/$name")
echo "$src"

pushd "$src" > /dev/null
mkdir -p build-ninja/.cmake/api/v1/query
touch build-ninja/.cmake/api/v1/query/codemodel-v2
if [ -f CMakePresets.json ]; then
  cmake -DCMAKE_EXPORT_COMPILE_COMMANDS=1 -S ./ --preset test
  src_root="$src"
else
  cmake -DCMAKE_EXPORT_COMPILE_COMMANDS=1 -S ./test_case -B ./build-ninja -G Ninja
  src_root="$src/test_case"
fi
popd > /dev/null

target_name=$(./get_target.py "$src/build-ninja" name)
target_type=$(./get_target.py "$src/build-ninja" type)
dst="$1/dst/$target_name"

if [[ "$target_type" == "EXECUTABLE" ]]; then
  ./filter_files.py "$src/build-ninja" "$src_root" "$src/build-ninja/compile_commands.json"
fi

mkdir -p "$dst"
c2rust-transpile -o "$dst" -e "$src/build-ninja/compile_commands.json"

./add_link_args.py "$src/build-ninja" "$dst/build.rs"

if [[ "$target_type" != "EXECUTABLE" ]]; then
  mkdir "$dst/.cargo"
  echo '[target.x86_64-unknown-linux-gnu]' > "$dst/.cargo/config.toml"
  echo 'rustflags = ["-Clink-arg=-Wl,-z,lazy", "-Zplt=yes"]' >> "$dst/.cargo/config.toml"
fi

tdst="$1/translated_rust"
cp -r "$dst" "$tdst"

if [[ "$target_type" == "EXECUTABLE" ]]; then
  crat \
    --inplace \
    --extern-cmake-reply-index-file "$src/build-ninja/.cmake/api/v1/reply/index-*.json" \
    --extern-build-dir "$src/build-ninja" \
    --extern-source-dir "$src" \
    --extern-ignore-return-type \
    --unsafe-remove-unused \
    --unsafe-remove-no-mangle \
    --unsafe-replace-pub \
    --bin-name "$target_name" \
    --pass expand,preprocess,extern,pointer,io,libc,static,unsafe,unexpand,split,bin \
    "$tdst"
else
  crat \
    --inplace \
    --unsafe-remove-unused \
    --unsafe-replace-pub \
    --pass expand,preprocess,extern,pointer,io,libc,static,unsafe,unexpand,split,bin \
    "$tdst"
  python3 cdylib.py "$tdst"
fi
