# Snippet Parser
The file `main.py` will read all snippets in the llvm dir on files listed by
`git diff main --name-only`.

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
