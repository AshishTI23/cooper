# -*- coding: utf-8 -*-
import ast
import pathlib
import re
import subprocess
import sys
import tokenize
import typing

__author__ = "¶¡rañha"

NOQA_RE = re.compile(r"# noqa", re.IGNORECASE)
rblog = pathlib.Path(__file__).parent.joinpath("..", "..").resolve().absolute()

source_paths = [
    rblog.joinpath("base"),
    rblog.joinpath("libs"),
    rblog.joinpath("common"),
    rblog.joinpath("brunch"),
]


class TopLevelProjImportVisitor(ast.NodeVisitor):
    def __init__(self, module, sources, init):
        self.imports = []
        self.bad_imports = []
        self.module = module
        self.sources = sources
        self.init = init

    def add_import(self, name, line_no):
        if name in self.sources:
            self.imports.append((name, line_no))
        else:
            a = name.split(".")[0]
            if a in self.sources:
                self.bad_imports.append((name, self.module))

    def visit_Import(self, node: ast.Import):
        if node.col_offset:
            return
        for imp in node.names:
            self.add_import(imp.name, node.lineno)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.col_offset:
            return

        node_module = node.module or ""
        if node.level:
            # convert relative import into absolute import
            level = node.level - self.init
            bases = self.module.split(".")
            if level:
                bases = self.module.split(".")[:-level]
            module = ".".join(filter(None, (*bases, node_module)))
        else:
            module = node_module

        should_add_top_module = False
        for imp in node.names:
            imported = ".".join((module, imp.name))
            # Hack to determine if the import is for module or any other object
            if imported in self.sources:
                # imported module
                self.add_import(imported, node.lineno)
            else:
                # imported variables
                should_add_top_module = True

        if should_add_top_module:
            self.add_import(module, node.lineno)


def get_modules(path: pathlib.Path) -> typing.Iterable[pathlib.Path]:
    for file_path in subprocess.run(
        ["git", "ls-files", "*.py"],
        cwd=path,
        capture_output=True,
        check=True,
        encoding="utf-8",
    ).stdout.splitlines():
        yield path / pathlib.Path(file_path)


def main():
    possible_imports = {}

    for path in source_paths:
        for file_ in get_modules(path):
            *parts, file_name = file_.relative_to(path).parts
            if "migrations" in parts:
                continue
            file_name = file_name[:-3]
            init_file = file_name == "__init__"
            if init_file:
                import_path = ".".join(parts)
            else:
                import_path = ".".join((*parts, file_name))
            possible_imports.setdefault(import_path, (file_, init_file))

    inprogress = []
    completed = set()
    cycles = set()
    bad_imports = set()

    def get_proj_imports(module, file_path: pathlib.Path, init) -> typing.Iterator[str]:
        with file_path.open(mode="r") as f:
            visitor = TopLevelProjImportVisitor(
                module=module,
                sources=possible_imports.keys(),
                init=init,
            )
            visitor.visit(ast.parse(f.read(), filename=str(file_path)))
            f.seek(0)
            noqa = set()
            for token_type, text, (line_no, _), _, _ in tokenize.generate_tokens(
                f.__next__
            ):
                if token_type == tokenize.COMMENT:
                    if NOQA_RE.search(text):
                        noqa.add(line_no)

        bad_imports.update(visitor.bad_imports)

        for import_, line_no in visitor.imports:
            if line_no not in noqa:
                yield import_

    def detect_cyclic_imports(module, file_path, init):
        if module in completed:
            return

        if module in inprogress:
            # cyclic import
            cycles.add(
                (*(map(str, inprogress[inprogress.index(module) :])), str(module))
            )
        else:
            inprogress.append(module)
            for import_module in get_proj_imports(
                module=module, file_path=file_path, init=init
            ):
                file_path, init = possible_imports[import_module]
                detect_cyclic_imports(
                    module=import_module,
                    file_path=file_path,
                    init=init,
                )
            inprogress.pop()
        completed.add(module)

    for mod, (file_, init_file) in possible_imports.items():
        detect_cyclic_imports(module=mod, file_path=file_, init=init_file)

    returncode = 0
    if cycles:
        returncode = 1
        print("Cyclic imports found")
        for cycle in cycles:
            print(*cycle, sep=" -> ")

    if bad_imports:
        returncode = 1
        for bad_import, module_ in bad_imports:
            print(f"Unable to resolve '{bad_import}' in {module_}")

    return returncode


if __name__ == "__main__":
    sys.exit(main())
