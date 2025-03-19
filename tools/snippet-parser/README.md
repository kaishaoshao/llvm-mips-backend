# Snippet Parser
The file `main.py` will read all snippets in the llvm dir on files listed by
`git diff main --name-only`.

## Running the snippet parser
`main.py` either runs on the LLVM source repo (whose must be in the `.env` file),
or can operate on a single file provided on the command line like so:

```bash
cd llvm-mips-tutorial
cd tools/snippet-parser
python3 main.py input.cpp [-d] [-o output.json]
```

### Testing
There are a few tests written using the `llvm-lit` and `FileCheck` tool to
test the parser. Look at `lit.cfg.py`.

> You will need the `lit` and `FileCheck` tool for this. Here is what I did:
> ```bash
> pip install --user lit # to install lit
> cd ../llvm-project
> cmake --build build --target FileCheck
> ```

Enter the path to the `FileCheck` binary in the `.env` file in the 
variable `FILECHECK_PATH`.
```env
FILECHECK_PATH="/path/to/bin/FileCheck"
```
Then you can run the lit tests:
```bash
cd llvm-mips-tutorial # root of this project
lit -sv tools/snippet-parser/tests
```

## Syntax
Snippets are code blocks enclosed by special comments prefixed by `@s` (to start 
a snippet) and `-` (to end the snippet).

For example, for `C++` files this is a valid snippet:
```cpp
//@s snippet-name <type>
function codeHere() { return value; }
//- snippet-name
```

For `CMakeLists.txt` files, use `#` for the comments as usual.
```py
#@s snippet
add_executable(main.cpp)
#- snippet
```

Snippets can take a type, specified after the snippet name.
```
<type> = "mark" | "removed" | <replace> | "end"
<replace> = "replace" "=" <snip-id>
<snip-id> = [^\s=]
```
Types are listed below.

### `mark`
With `mark`, the snippet will be highlighted with a mark range intead of
a diff addition range. (use this for highlighting code that is not to be
added or removed)

### `end`
Type `end` means no after-context will be shown in the final code snippet.

### `removed`
This will be shown as a removed diff in the snippet.

### `replace=snip-id`
If type is "removed", leading comments in the snippet
will be removed while rendering in CodeSnippet.astro
