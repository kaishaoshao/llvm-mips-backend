# the snippets format is
# //@s snippet-name <type>
# //- snippet-name
# <type> = "mark" | "removed" | <replace> | "end"
# "end" => no after context should be shown
# <replace> = "replace" "=" <snippet-id-this-replaces>
# If type is "removed", leading comments in the snippet
# will be removed while rendering in CodeSnippet.astro

# If type is "replace", the <snippet-id-this-replaces> will be shown
# as a deleted diff in the CodeSnippet.astro, with the current snippet
# as the added diff.

# Snippets should not be nested.
# This script extracts all snippets and writes them to
# snippets.json file.

from dotenv import load_dotenv
import os
import argparse
import logging
import subprocess
import types
import sys
from pathlib import Path
import re
from enum import Enum, auto
import json
import time

debug = False
logger = logging.getLogger(__name__)
load_dotenv()
LLVM_ROOT_DIR = os.environ.get("LLVM_ROOT_DIR")


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


IGNORE_FILES = ['.png']


def get_abs_filenames(llvm_dir: Path):
    """
    Get relative file paths for the changed files 
    in the LLVM root tree
    """

    command = "git diff main --name-only".split(" ")
    logger.info(" ".join(command))
    res = subprocess.run(command, capture_output=True, cwd=llvm_dir)
    filenames = res.stdout.decode().strip().split("\n")
    filenames = [llvm_dir/Path(f) for f in filenames]
    # filter with suffixes
    filenames = [f for f in filenames if f.suffix not in IGNORE_FILES]
    return filenames


def get_reg_start(comment_chars: str):
    return r'^\s*' + comment_chars


class Regexes:
    cpp_comments_filext = ['.cpp', '.h', '.td']
    hash_comments_filext = ['.txt']
    cpp_prefix = get_reg_start("//")
    cmake_prefix = get_reg_start("#")
    start_suffix = r'@s\s+(?P<name>[^ \s]+)(?P<type>\s+[^\s=]+(=[^=\s]+)?)?\s*$'
    end_suffix = r'-\s+([^ ]+)\s*\n?$'

    # is for Triple::Triple(something) constructor syntax
    endings = ['{', '(', ',', ')']
    keywords = ['for', 'if', 'while', 'switch']

    multiline_end = re.compile(r'^\s*[^)\n]+\)[^\n]*(;|(\{\}))?$')

    start_regex = re.compile(cpp_prefix + start_suffix)
    end_regex = re.compile(cpp_prefix + end_suffix)

    td_start_regex = re.compile(cmake_prefix + start_suffix)
    td_end_regex = re.compile(cmake_prefix + end_suffix)

    ll_start_regex = re.compile(get_reg_start(";") + start_suffix)
    ll_end_regex = re.compile(get_reg_start(";") + end_suffix)

    function_pattern = re.compile(
        r'((?:template\s*<.*>\s*)?(?:\w+(?:::\w+)*\s+)+\w+\s*\([^)]*\)(?:\s*const)?(?:\s*noexcept)?(?:\s*override)?(?:\s*final)?(?:\s*=\s*default)?(?:\s*=\s*delete)?)\s*{')
    multiline_function = re.compile(
        r'((?:template\s*<.*>\s*)?(?:\w+(?:::\w+)*\s+)+\w+\s*\([^),]*,)')
    extern_c = re.compile(r'^\s*extern "C" .+\(')
    new_function_pattern = re.compile(
        r'''^(?:\stemplate\s<[^>]+>\s*)? # optional template clause
(?:[\w:&<>_*\s]+\s+)? # optional return type (and qualifiers/pointers/references)
\s* # optional whitespace
(?P<name>[*&]*[_\w:~]+(==|!=|\*)?) # capture the function name (may include scope :: and destructor ~)
\s* # optional whitespace
\([^!;{,]* # a literal '(' plus “stuff” that isn’t ; { or ,
(?:,.+)? # optional comma and more stuff
[,{(]? # then either a { or a , or ( (the latter for multi‐line)
$''', re.VERBOSE)


def get_indent(line: str):
    return line.find(line.strip())


class Context:
    ONLY_INCLUDE_FILES = ['.cpp', '.h']

    class Type(Enum):
        NONE = 20
        AFTER = 12  # this is for top level contexts outside namespaces
        # used to show "after <decl>" contexts.
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
        self.line = line.strip()
        self.type: FileSnippetReader.Context.Type = type
        self.inner: Context = None
        self.lineno = lineno
        self.indent = get_indent(line)

    def copyWith(self, type):
        return Context(self.line, type, self.lineno)

    def __repr__(self):
        return f"[:{self.lineno}] {self.line}"

    # override the less than operator
    def __lt__(self, other):
        return self.type <= other.type

    def to_dict(self):
        return {
            # "content": self.line,
            "type": self.type.name,
            "line": self.lineno
        }


class Snippet:
    def __init__(self, name, type: str, filename, start_lineno, end_lineno=None, context_stack=[]):
        self.name = name
        self.type = type
        if self.type is None:
            self.type = "add"
        self.type = self.type.strip()
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
            "context_stack": [c.to_dict() for c in self.context_stack],
            "type": self.type
        }


class Statistics:
    def __init__(self):
        self.snippets = 0
        self.files = 0

    def addSnippet(self):
        self.snippets += 1

    def addFile(self):
        self.files += 1

    def print(self):
        print(f"Statistics:")
        print(f"\t{self.snippets} snippets from {self.files} files.")


STATS = Statistics()


class FileSnippetReader:
    def __init__(self, filepath: Path, relative_filepath_str: str = None):
        """
        relative_filepath_str: Path to print in the JSON
        """
        self.filepath = filepath
        self.relative_filepath_str = relative_filepath_str
        if relative_filepath_str is None:
            self.relative_filepath_str = filepath.absolute().as_posix()
        # This points to the next line.
        # Current line is at self.i - 1, use self.peek_line() instead though.
        self.i = 0
        self.context_stack: List[Context] = []
        self.last_context: Context = None
        self.char_i = 0
        self.snippets = self.extract_file_snippets(filepath)

    def to_dict(self):
        return [s.to_dict() for s in self.snippets]

    def peek_line(self):
        return self.lines[self.i-1]

    def clineno(self):
        """ Current line number ( 1 indexed)"""
        return self.i

    def consume_line(self):
        self.i += 1
        return self.lines[self.i - 1]

    def is_at_end(self):
        return self.i == len(self.lines)

    def get_line(self, i):
        return self.lines[i]

    def get_last_after_context(self):
        # print("\tafter======")
        if self.last_context is None:
            # print('where')
            return Context("", Context.Type.NONE, 0)
        return self.last_context.copyWith(Context.Type.AFTER)

    def get_regex(self, start: bool):
        if self.filepath.suffix in Regexes.cpp_comments_filext:
            return Regexes.start_regex if start else Regexes.end_regex
        elif self.filepath.suffix in Regexes.hash_comments_filext:
            return Regexes.td_start_regex if start else Regexes.td_end_regex
        elif self.filepath.suffix in ['.ll', '.s']:
            return Regexes.ll_start_regex if start else Regexes.ll_end_regex
        else:
            # throw error
            logger.fatal(Colors.error(
                f"Error: Unknown file extension {self.filepath.suffix}"))
            sys.exit(1)

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
                line = self.consume_line()
                lineno = self.clineno()
                self.consume_context()
                self.print_context()
                # continue
                # end header
                start_match = self.get_regex(start=True).match(line)
                end_match = self.get_regex(start=False).match(line)
                if start_match:
                    the_context = self.context_stack.copy()
                    if the_context.__len__() == 0:
                        the_context.append(self.get_last_after_context())
                    stack.append(Snippet(name=start_match.group("name"),
                                         type=start_match.group("type"),
                                         filename=self.relative_filepath_str,
                                         start_lineno=lineno,
                                         end_lineno=None,
                                         context_stack=the_context))
                elif end_match:
                    if not stack:
                        logger.error(
                            f"{Colors.RED}Error: line {lineno}: Found end snippet without start")
                        logger.error(f"Snippet name: {end_match.group(1)}")
                        logger.error(
                            f"Snippet file: {self.filepath}{Colors.ENDC}")
                        sys.exit(1)
                    end_line = lineno
                    top_snip = stack[-1]
                    if end_match.group(1).strip() != top_snip.name:
                        logger.error(
                            f"{Colors.RED}Error: line {lineno}: Found end snippet without start")
                        logger.error(f"Snippet name: '{end_match.group(1)}'")
                        logger.error(
                            f"Previous snippet name: '{top_snip.name}'")
                        logger.error(
                            f"Snippet file: {self.filepath}{Colors.ENDC}")
                        sys.exit(1)
                    snippets.append(stack.pop().withEndLine(end_line))

                # self.print_context()
            if stack:
                logger.error(
                    f"{Colors.RED}Error: line {self.clineno()}: Found start snippet without end")
                logger.error(f"Snippet name: '{stack[-1].name}'")
                logger.error(f"Snippet file: {self.filepath}{Colors.ENDC}")
                sys.exit(1)
            return snippets

    def print_context(self):
        if not debug:
            return
        print(f"Context[{self.clineno()}]:")
        for i, c in enumerate(self.context_stack):
            indent = " " * i
            print(indent + c.__repr__())
        print("===end context===")

    def is_ending_brace(self, line):
        line = line.strip()
        comments = line.split("//")
        if len(comments) > 2:
            return False
        line = comments[0]
        return line.strip().startswith("}")

    def ends_with_open_brace(self, line):
        line = line.strip()
        comments = line.split("//")
        if len(comments) > 2:
            return False
        line = comments[0]
        return line.strip().endswith("{")

    def consume_context(self):
        if self.filepath.suffix not in Context.ONLY_INCLUDE_FILES:
            return

        # attempt to read the context
        # context can be a function or enum or class
        # line = self.lines[self.i]
        class_regex = re.compile(r'^\s*(template<.+>)?\s?class')
        class_forward = re.compile(
            r'^\s*(template<.+>\s?)?class\s+[\w_\d]+\s*;')
        struct_regex = re.compile(r'^\s*(template<.+>)?\s+struct')
        if not self.is_at_end():
            line = self.peek_line().strip()
            # check for class
            context_type = None
            if line.startswith("//"):
                return
            elif line.startswith("#ifdef"):
                context_type = Context.Type.ANONYMOUS
            elif line.startswith("class") or (line.endswith("{") and "class " in line):
                # ignore forward declarations
                if class_forward.match(line):
                    return
                context_type = Context.Type.CLASS
            elif line.startswith("namespace"):
                context_type = Context.Type.NAMESPACE
            elif line.startswith("enum"):
                context_type = Context.Type.ENUM
            elif line.startswith("struct") or (line.endswith("{") and "struct " in line):
                context_type = Context.Type.STRUCT
            elif line.startswith("union"):
                context_type = Context.Type.UNION
            else:
                # check for function
                f_match = Regexes.new_function_pattern.match(line)
                if f_match:
                    # get the ?P capture group
                    fname = f_match.group("name")
                    if fname not in Regexes.keywords and line[-1] in Regexes.endings:
                        # print("\t== found function at line", self.clineno(), self.filepath)
                        # print("\t== ?P name: ", f_match.group("name"))
                        context_type = Context.Type.FUNCTION
                elif Regexes.extern_c.match(line):
                    # or Regexes.multiline_function.match(line):
                    context_type = Context.Type.FUNCTION
                    # print("\t== found function at line", self.clineno(), self.filepath)
                elif self.ends_with_open_brace(line):
                    till_open_paren = line.find("(")
                    if till_open_paren > 0:
                        # print("Found open paren substr: ", line[:till_open_paren].strip() == "for")
                        func_name = line[:till_open_paren].strip()
                        if func_name not in Regexes.keywords:
                            context_type = Context.Type.ANONYMOUS
            if context_type:
                # print("found a context: ", line)
                self.context_stack.append(
                    Context(self.peek_line(), context_type, self.clineno()))

                if self.has_same_line_body(line):
                    # print("empty body")
                    self.context_stack.pop()
            else:
                # check for end of context
                if self.is_ending_brace(line):
                    if self.context_stack.__len__() > 0:
                        current_indent = get_indent(self.peek_line())
                        while len(self.context_stack) > 0:
                            top = self.context_stack[-1]
                            if top.indent == current_indent:
                                self.context_stack.pop()
                                break
                            elif top.indent > current_indent:
                                self.context_stack.pop()
                                # print(
                                #     f"\t===popped for line:{self.clineno()}, {top.line}")
                            else:
                                logger.warning(
                                    f"Error: unmatched }} at line {self.clineno()}")
                                logger.warning(f"in file: {self.filepath}")
                                logger.warning(
                                    f"This may be due to a nested block. Currently this script does not handle them.")
                                break
                        # top = self.context_stack[-1]
                        # if top.indent == self.peek_line().find(self.peek_line().strip()):
                        #     self.context_stack.pop()
                        #     print(
                        #         f"\t===popped for line:{self.clineno()}, {top.line}")
                    else:
                        logger.warning(f"Error: unmatched }} at line {self.clineno()}\nFile: {self.filepath}")
                        # sys.exit(1)
        if len(self.context_stack) > 0:
            self.last_context = self.context_stack[-1]
        return

    def lookahead_multiline_decl(self):
        """Current line is a multiline function declaration
        and ends with a ','. This function will consume
        next lines till ';' or '{' is found.
        Returns if the function is a multiline function.
        """
        # to restore if we fail
        orig_i = self.i
        line_endings = [',', '(', '"']
        while not self.is_at_end():
            next_line = self.consume_line().strip()
            is_still_multiline = False
            for e in line_endings:
                if next_line.endswith(e):
                    is_still_multiline = True
                    break
            if is_still_multiline:
                continue
            elif Regexes.multiline_end.match(next_line):
                return True
            elif next_line.endswith('{'):
                return False
            else:
                logger.warning(Colors.error(
                    f"Error: multiline decl ends abruptly at line {self.clineno()}"))
                logger.warning(f"File: {self.filepath}")
                # sys.exit(1)
        return False

    def has_same_line_body(self, line: str):
        """ Must have {.*} on the same line
            or ends with a ';' (for multiline function decls)
        """
        if line.endswith(','):
            # print("found multiline function")
            return self.lookahead_multiline_decl()
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
    all_snippets = []
    STATS.files = len(filepaths)
    for file in filepaths:
        rel_path = file.relative_to(llvm_dir).as_posix()
        fileReader = FileSnippetReader(file, rel_path)
        all_snippets.extend(fileReader.to_dict())

    STATS.snippets += len(all_snippets)
    return all_snippets

def parse_args(args):
    parser = argparse.ArgumentParser(
        description="Snippet parser for the LLVM codebase"
    )

    parser.add_argument("-o", "--output", type=str,
                        default="-", help='Output JSON filename')
    parser.add_argument("input", nargs="?", type=str,
                        help="Path to the input file. If not provided, the LLVM code will be taken.")
    parser.add_argument("-d", "--dump-contexts", action="store_true",
                        help="Enable debug mode", default=False)
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Enable logging", default=False)
    parser.add_argument("--diff", action="store_true", help="Print the diff file list that would be scanned otherwise",
                        default=False)
    return parser.parse_args(args)


def writeOut(snippets: dict, filename: str):
    # if filename is -, write to stdout
    if filename == "-":
        print(json.dumps(snippets, indent=2))
    else:
        with open(filename, "w") as f:
            json.dump(snippets, f, indent=2)
        print(f"Written to {filename}")
        STATS.print()
        print(f"{Colors.BLUE}\tin {time.time() - START_TIME} seconds.")

def main(llvm_dir_path: Path):
    all_snippets = extract_all_snippets_from_dir(llvm_dir_path)
    return all_snippets
    # fileReader = FileSnippetReader(Path(llvm_dir_path))
    # print(fileReader.to_dict())


START_TIME = 0


def driver():
    global START_TIME
    START_TIME = time.time()
    # git_dir = "/home/mirasma/Projects/llvm-project"
    example_path = Path("./example.txt")
    args = parse_args(sys.argv[1:])

    if args.verbose:
        level = logging.INFO
    else:
        level = logging.CRITICAL
    if args.dump_contexts:
        level = logging.DEBUG
    logging.basicConfig(level=level)

    if args.diff:
        print(get_abs_filenames(LLVM_ROOT_DIR))
        return 0

    # logging.info(args)
    global debug
    debug = args.dump_contexts
    all_snips = {}
    if args.input is not None:
        all_snips = FileSnippetReader(Path(args.input)).to_dict()
        # writeOut(snippets.to_dict(), args.output)
    else:
        if LLVM_ROOT_DIR:
            all_snips = main(Path(LLVM_ROOT_DIR))
        else:
            print("Error: LLVM_ROOT_DIR is not set in the environment")
            return 1

    writeOut(all_snips, args.output)
    return 0


if __name__ == "__main__":
    sys.exit(driver())
