#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0
"""Regenerate the two lists kleaf hands to the GKI kernel_aarch64 build.

make builds of this tree read them through vendor/pong_GKI.config:
  android/abi_symbollist.raw         CONFIG_UNUSED_KSYMS_WHITELIST
                                     (gki/aarch64/symbols/base + the
                                     aarch64_additional_kmi_symbol_lists of
                                     BUILD.bazel, flattened)
  android/protected_module_names_list CONFIG_MODULE_SIG_PROTECT_LIST
                                     (get_gki_protected_modules_list("arm64")
                                     of modules.bzl, without .ko)

Run from anywhere after touching gki/aarch64/symbols, BUILD.bazel or modules.bzl.
"""
import ast
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def symbol_lists():
    build = open(os.path.join(ROOT, "BUILD.bazel")).read()
    m = re.search(r'name = "aarch64_additional_kmi_symbol_lists",\s*srcs = \[(.*?)\]', build, re.S)
    extra = re.findall(r'"([^"]+)"', m.group(1))
    return ["gki/aarch64/symbols/base"] + extra


def flatten(paths):
    syms = set()
    for p in paths:
        for line in open(os.path.join(ROOT, p)):
            line = line.split("#", 1)[0].strip()
            if line and not line.startswith("["):
                syms.add(line)
    return sorted(syms)


def protected_modules():
    # modules.bzl is plain Starlark: evaluate it with Python, Starlark list views
    src = open(os.path.join(ROOT, "modules.bzl")).read()
    src = re.sub(r'^load\(.*?\)\n', "", src, flags=re.M | re.S)
    ns = {"select": lambda d: [], "struct": lambda **k: k, "fail": lambda *a: (_ for _ in ()).throw(Exception(a))}
    exec(compile(ast.parse(src), "modules.bzl", "exec"), ns)
    return [m.removesuffix(".ko") for m in ns["get_gki_protected_modules_list"]("arm64")]


def write(name, lines):
    with open(os.path.join(ROOT, "android", name), "w") as f:
        f.write("\n".join(lines) + "\n")


write("abi_symbollist.raw", flatten(symbol_lists()))
write("protected_module_names_list", protected_modules())
