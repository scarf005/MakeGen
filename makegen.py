#!/bin/env python3

import re
import textwrap
from pathlib import Path


def get_subdirs(path: Path):
    yield from (p for p in path.glob("[!.]*") if p.is_dir())


def get_src_files(subdir: Path):
    yield from (p for p in subdir.glob("*.c"))


def make_var(name: str, values: list[str]) -> str:
    name_len = len(name)
    wrapped = textwrap.wrap(" ".join(values), 70 - name_len)
    wrapped_len = len(wrapped)
    if wrapped_len == 0:
        return ""
    pad = "\t" * ((name_len + 3) // 4)
    res = f"{name} = {wrapped[0]}"
    if wrapped_len > 1:
        res += "\\"
    for w in wrapped[1:-1]:
        res += f"\n{pad}{w}\\"
    if wrapped_len > 1:
        res += f"\n{pad}{wrapped[-1]}"
    res += "\n"
    return res


def create_values(subdir: Path) -> str:
    values = [s.stem for s in get_src_files(subdir)]
    return make_var(f"{subdir.name.replace('std__', '')}V", values)


def create_template(path: Path) -> str:
    subdirs = [s for s in get_subdirs(path)]
    packages = [s.name.replace("std__", "") for s in subdirs]
    res = make_var("PKGS", packages) + "\n"
    for subdir in subdirs:
        res += create_values(subdir)
    return res


def regex_index(lst: list[str], pattern: str, flags=0):
    for i, line in enumerate(lst):
        if re.match(pattern, line, flags):
            return i
    raise ValueError(f"{pattern} not found in {lst}")


def replace_text(
    text: str,
    to_replace: str,
    begin_text: str = r"#\s*@packages",
    end_text: str = "#",
) -> str:
    lines = text.splitlines()
    begin = 1 + regex_index(lines, begin_text, re.I)
    end = begin + regex_index(lines[begin:], end_text, re.I)
    # replace lines
    lines[begin:end] = [to_replace]
    return "\n".join(lines)

def makegen(src_dir: Path = Path('src'), makefile: Path = Path('Makefile')):
    template = create_template(src_dir)
    text = makefile.read_text()
    makefile.write_text(replace_text(text, template))

def main():
    makegen()

if __name__ == "__main__":
    main()
