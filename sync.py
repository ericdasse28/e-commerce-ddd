import hashlib
import os
import shutil
from pathlib import Path

BLOCKSIZE = 65536


def sync(source, dest):
    # Imperative shell step 1, gather inputs
    source_hashes = read_paths_and_hashes(source)
    dest_hashes = read_paths_and_hashes(dest)

    # Step 2: call functional core
    actions = determine_actions(source_hashes, dest_hashes, source, dest)

    # Imperative shell step 3, apply accounts
    for action, *paths in actions:
        if action == "COPY":
            shutil.copyfile(*paths)

        if action == "MOVE":
            shutil.move(*paths)

        if action == "DELETE":
            os.remove(paths[0])


def read_paths_and_hashes(root):
    hashes = {}
    for folder, _, files in os.walk(root):
        for fn in files:
            hashes[hash_file(Path(folder) / fn)] = fn

    return hashes


def hash_file(path: Path):
    hasher = hashlib.sha1()
    with path.open("rb") as file:
        buf = file.read(BLOCKSIZE)
        while buf:
            hasher.update(buf)
            buf = file.read(BLOCKSIZE)

    return hasher.hexdigest()


def determine_actions(
    source_hashes: dict,
    dest_hashes: dict,
    source_folder: str,
    dest_folder: str,
):
    for sha, filename in source_hashes.items():
        if sha not in dest_hashes:
            source_path = Path(source_folder) / filename
            dest_path = Path(dest_folder) / filename
            yield "COPY", source_path, dest_path

        elif dest_hashes[sha] != filename:
            old_dest_path = Path(dest_folder) / dest_hashes[sha]
            new_dest_path = Path(dest_folder) / filename
            yield "MOVE", old_dest_path, new_dest_path

    for sha, filename in dest_hashes.items():
        if sha not in source_hashes:
            yield "DELETE", dest_folder / filename
