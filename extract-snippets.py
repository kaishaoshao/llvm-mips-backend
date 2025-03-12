# the snippets format is
# // l2m-snip-start snippet-name
# // l2m-snip-end snippet-name
# Snippets should not be nested.
# This script extracts all snippets and writes them to
# snippets.json file.

import subprocess
import types
import sys
from pathlib import Path
import re
from enum import Enum, auto
import json


class Colors:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    ENDC = "\033[0m"

    def error(msg):
        return f"{Colors.RED}{msg}{Colors.ENDC}"


def generate_lines(filename):
    with open(filename) as f:
        for line in f:
            yield line


def get_abs_filenames(llvm_dir: Path):
    """
    Get relative file paths for the changed files 
    in the LLVM root tree
    """

    command = "git diff main --name-only".split(" ")
    print(" ".join(command))
    res = subprocess.run(command, capture_output=True, cwd=llvm_dir)
    filenames = res.stdout.decode().strip().split("\n")
    print(filenames)
    filenames = [llvm_dir/Path(f) for f in filenames]
    return filenames


class Regexes:
    start_regex = re.compile(r'^\s*\/\/\@s\s+([^ \s]+)\s*$')
    function_pattern = re.compile(
        r'((?:template\s*<.*>\s*)?(?:\w+(?:::\w+)*\s+)+\w+\s*\([^)]*\)(?:\s*const)?(?:\s*noexcept)?(?:\s*override)?(?:\s*final)?(?:\s*=\s*default)?(?:\s*=\s*delete)?)\s*{')
    multiline_function = re.compile(
        r'((?:template\s*<.*>\s*)?(?:\w+(?:::\w+)*\s+)+\w+\s*\([^),]*,)')
    end_regex = re.compile(r'\s*\/\/\-\s+([^ ]+)\s*$')
    new_function_pattern = re.compile(
        r'''^(?:\stemplate\s<[^>]+>\s*)? # optional template clause
(?:[\w:&<>*\s]+)? # optional return type (and qualifiers/pointers/references)
\s* # optional whitespace
(?P<name>[\w:~]+) # capture the function name (may include scope :: and destructor ~)
\s* # optional whitespace
\([^;{,]* # a literal '(' plus “stuff” that isn’t ; { or ,
[,{(] # then either a { or a , or ( (the latter for multi‐line)
$''', re.VERBOSE)


class Context:
    class Type(Enum):
        NAMESPACE = 11
        CLASS = 10
        ENUM = 9
        STRUCT = 9
        UNION = 9
        FUNCTION = 8
        ANONYMOUS = 7
        SWITCH = 7
        IF_ELSE = 7

    def __init__(self, line, type, lineno):
        self.line = line
        self.type: FileSnippetReader.Context.Type = type
        self.inner: Context = None
        self.lineno = lineno
        self.indent = line.find(line.strip())

    def __repr__(self):
        return f"[:{self.lineno}]: {self.line}"

    # override the less than operator
    def __lt__(self, other):
        return self.type <= other.type

    def to_dict(self):
        return {
            "line": self.line,
            "type": self.type.name,
            "line": self.lineno
        }


class Snippet:
    def __init__(self, name, filename, start_lineno, end_lineno=None, context_stack=[]):
        self.name = name
        self.filename = filename
        self.start_lineno = start_lineno
        self.end_lineno = end_lineno
        self.code = ""
        self.context_stack = context_stack

    def __repr__(self):
        s = f"Snippet {self.name} in {self.filename}:{self.start_lineno}-{self.end_lineno}"
        s += f"\nContext: {self.context_stack}"
        return s

    def withEndLine(self, end_lineno):
        self.end_lineno = end_lineno
        return self

    def to_dict(self):
        return {
            "id": self.name,
            "filename": self.filename,
            "start_lineno": self.start_lineno,
            "end_lineno": self.end_lineno,
            "context_stack": [c.to_dict() for c in self.context_stack]
        }


class FileSnippetReader:
    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.i = 0
        self.context_stack: List[Context] = []
        self.char_i = 0
        self.snippets = self.extract_file_snippets(filepath)

    def to_dict(self):
        return [s.to_dict() for s in self.snippets]

    def peek_line(self):
        return self.lines[self.i]

    def clineno(self):
        """ Current line number"""
        return self.i + 1

    def consume_line(self):
        self.i += 1
        return self.lines[self.i - 1]

    def is_at_end(self):
        return self.i == len(self.lines)

    def extract_file_snippets(self, filepath: Path):
        """
        filepath: full path to the file
        """
        snippets: List[Snippet] = []
        stack: List[Snippet] = []
        current_context: str = None

        with open(filepath, 'r') as f:
            self.lines = f.readlines()
            # begin loop
            self.i = 0
            while not self.is_at_end():
                lineno = self.clineno()
                line = self.consume_line()
                self.consume_context()
                self.print_context()
                # continue
                # end header
                start_match = Regexes.start_regex.match(line)
                end_match = Regexes.end_regex.match(line)
                if start_match:
                    # print("found match with context as ", len(self.context_stack))
                    stack.append(Snippet(name=start_match.group(1),
                                         filename=filepath.absolute().as_posix(),
                                         start_lineno=lineno,
                                         end_lineno=None,
                                         context_stack=self.context_stack.copy()))
                elif end_match:
                    if not stack:
                        print(f"Error: line {lineno}: Found end without start")
                        print(f"Snippet name: {end_match.group(1)}")
                        print(f"Snippet file: {filename}")
                        sys.exit(1)
                    end_line = lineno
                    snippets.append(stack.pop().withEndLine(end_line))

                # self.print_context()

            return snippets

    def print_context(self):
        return
        print("=== context At line: ", self.i + 1, "===")
        for c in self.context_stack:
            print(c)
            print("\n")
        print("==== context over ====")

    def consume_context(self):
        # attempt to read the context
        # context can be a function or enum or class
        # line = self.lines[self.i]
        if not self.is_at_end():
            line = self.peek_line().strip()
            # check for class
            context_type = None
            if line.startswith("//"):
                return
            elif line.startswith("class"):
                context_type = Context.Type.CLASS
            elif line.startswith("namespace"):
                context_type = Context.Type.NAMESPACE
            elif line.startswith("enum"):
                context_type = Context.Type.ENUM
            elif line.startswith("struct"):
                context_type = Context.Type.STRUCT
            elif line.startswith("union"):
                context_type = Context.Type.UNION
            else:
                # check for function
                if Regexes.new_function_pattern.match(line) or Regexes.multiline_function.match(line):
                    context_type = Context.Type.FUNCTION
            if context_type:
                # print("found a context: ", line)
                self.context_stack.append(
                    Context(line, context_type, self.clineno()))

                if self.has_same_line_body(line):
                    # print("empty body")
                    self.context_stack.pop()
            else:
                # check for end of context
                if line.startswith("}"):
                    if self.context_stack.__len__() > 0:
                        top = self.context_stack[-1]
                        if top.indent == self.peek_line().find(self.peek_line().strip()):
                            self.context_stack.pop()
                            print(
                                f"popped for line:{self.clineno()}, {top.line}")
                    else:
                        print(Colors.error(
                            "Error: unmatched } at line "), self.clineno())
                        print(f"File: {self.filepath}")
                        sys.exit(1)
        return

    def has_same_line_body(self, line):
        """ Must have {.*} on the same line"""
        i = 0
        stack_length = 0
        body_length = 0
        brace_count = 0
        for i in range(0, len(line)):
            if line[i] == '{':
                stack_length += 1
                brace_count += 1
            elif line[i] == '}':
                stack_length -= 1
            else:
                if stack_length > 0:
                    body_length += 1
        return stack_length == 0 and brace_count > 0


def extract_all_snippets_from_dir(llvm_dir: Path):
    filepaths = get_abs_filenames(llvm_dir)
    print(filepaths)
    for file in filepaths:
        fileReader = FileSnippetReader(file)
        print(fileReader.to_dict())
    return


def main(llvm_dir_path: Path):
    extract_all_snippets_from_dir(llvm_dir_path)
    return
    # fileReader = FileSnippetReader(Path(llvm_dir_path))
    # print(fileReader.to_dict())
    with open("snippets.json", "w") as f:
        json.dump(fileReader.to_dict(), f, ensure_ascii=True, indent=2)
    return


if __name__ == "__main__":
    git_dir = "/home/mirasma/Projects/llvm-project"
    example_path = Path("./example.txt")
    if len(sys.argv) > 1 and sys.argv[1] == "-e":
        main(example_path)
    else:
        main(Path(git_dir))
