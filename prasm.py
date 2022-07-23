#!/usr/bin/env python3
from odf.opendocument import load
from odf import text, teletype
from odf.element import Element
import os.path
import struct
import platform
import shlex
import subprocess

Page_Attribute = ('urn:oasis:names:tc:opendocument:xmlns:drawing:1.0', 'name')
Class_Attribute = ('urn:oasis:names:tc:opendocument:xmlns:presentation:1.0', 'class')

# Calculate platform bitness based on size of a pointer
# If result is weird default to 32 bits
Bits = struct.calcsize("P") * 8
if Bits not in [32, 64]:
    Bits = 32

# Match user system as NASM target. Default is Unix-like (supporting elf),
# so dispatch for weird cases
Target = { "Darwin": f"macho", "Windows": f"win" }.get(platform.system(), "elf") + str(Bits)
Exe_Suffix = ".exe" if platform.system() == "Windows" else ".out"

def main(source: str, output: str, assembly: str, nasm: str, object: str, ld: str):
    with open(assembly, 'w') as out:
        pres = load(source)

        print(f"BITS {Bits}",  file=out)
        print("segment .text", file=out)
        print("global _start", file=out)

        for page in pres.getElementsByType(text.P):
            if not match_parent_node(page, tag_name='draw:page') or match_parent_node(page, attribute=(Page_Attribute, 'page1')):
                continue

            if match_parent_node(page, 'text:list-item'):
                # This are regular list nodes
                print(teletype.extractText(page).lower(), file=out)

            if match_parent_node(page, attribute=(Class_Attribute, 'title')):
                # This are titles
                print(mangle_label(teletype.extractText(page)), file=out)

    cmd(nasm, "-f", Target, "-o", object, assembly)
    cmd(ld, "-o", output, object)

def mangle_label(label: str) -> str:
    return label + ":"

def iterate_parents(node: Element):
    while node.parentNode:
        yield node
        node = node.parentNode

def find_parent_node(node: Element, /, tag_name: str | None = None, attribute: tuple | None = None) -> Element | None:
    "Find parent node with appropiate tag name or attribute, depending on which are specified"
    required = int(tag_name is not None) + int(attribute is not None)

    if attribute is not None:
        attr_key, attr_val = attribute
    else:
        # They should be never used but linter would scream at me if i don't include them
        attr_key, attr_val = None, None

    for parent in iterate_parents(node):
        satisfied = int(parent.tagName == tag_name)
        satisfied += int(bool(attribute and parent.attributes.get(attr_key) == attr_val))

        if required == satisfied:
            return node

def match_parent_node(*args, **kwargs) -> bool:
    return find_parent_node(*args, **kwargs) is not None

def get_path_of(node: Element):
    "Returns path of element based on parent nodes"
    return ' / '.join(node.tagName for node in reversed(list(iterate_parents(node))))

def parents_dump(node: Element):
    print(50 * "-")
    print("Parents dump")
    print(50 * "-")

    for p in iterate_parents(node):
        print("Tag: ", p.tagName)
        print("Attr:", p.attributes)
        print("Text:", teletype.extractText(p))
        print()

def cmd(*command: str, **kwargs) -> subprocess.CompletedProcess:
    if Verbose:
        print("[CMD] %s" % " ".join(map(shlex.quote, command)))
    return subprocess.run(command, **kwargs)

def replace_extension(p: str, ext: str) -> str:
    return f"{os.path.splitext(p)[0]}{ext}"

if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser(description="Assembler of PRASM assembly language")
    parser.add_argument("source", help="Source file that will be assembled")
    parser.add_argument("--output", "-o", help="Target assembly file")
    parser.add_argument("--nasm", help="Path to NASM")
    parser.add_argument("--linker", help="Path to linker", dest="ld")
    parser.add_argument("--tmpasm", help="Path for intermidiate assembly output", dest="assembly")
    parser.add_argument("--tmpobj", help="Path for intermidiate object file", dest="object")
    parser.add_argument("-V", "--verbose", help="Print all info", action="store_true")
    args = parser.parse_args()

    if args.output   is None: args.output   = replace_extension(args.source, Exe_Suffix)
    if args.assembly is None: args.assembly = replace_extension(args.source, ".nasm")
    if args.object   is None: args.object   = replace_extension(args.source, ".o")
    if args.nasm     is None: args.nasm     = "nasm"
    if args.ld       is None: args.ld       = "ld"
    Verbose = args.verbose

    main(**dict(k for k in vars(args).items() if k[0] not in ['verbose'] ))
