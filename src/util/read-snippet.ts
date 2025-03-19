import { z } from "astro:content";
import fs from "node:fs/promises"
import { after } from "node:test";

const SURROUNDING_CONTEXT_LINES = 2;
const LLVM_ROOT_DIR_NAME = "llvm-project"

/// This is the snippet type in snippets.json
export const snippetType = z.object({
    id: z.string(),
    start_lineno: z.number(),
    end_lineno: z.number(),
    filename: z.string(),
    context_stack: z.array(z.object({
        line: z.number(),
        type: z.string(),
    })),
    //type has values "add","replace"
    type: z.string(),
})

interface Range {
    /// The line number to start this range from
    /// (inclusive, 1-indexed)
    start: number;
    /// Number of lines to read (including the
    /// start line)
    /// Needs to be minimum one
    numLines: number;
}

async function readLines(filename: string, ranges: Range[]) {
    const text = await fs.readFile(filename, "utf-8");
    // create array the same length of lines
    const lineTexts: string[] = new Array(ranges.length);
    // Subtract one from each start since it starts from 1
    // and we count from 0
    ranges.forEach(range => range.start = range.start - 1)
    for (let i = 0; i < text.length; i++) {

    }
}

interface SnippetContent {
    snippet: string; // the main content
    contextStack: { // stack of contexts
        text: string; // the main context content
        type: string;
    }[];
    filename: string, // The absolute file path
    surrounding: {
        lines: number;
        before: string;
        after: string;
    }
}

interface Context {
    text: string;
    type: string;
}

function preProcessContexts(contexts: Context[]): string[] {
    return contexts.map((c, i) => {
        // if (c.type == "FUNCTION") {
        //     const fnName = c.text.split("(")[0].split(" ").at(-1);
        //     return "func " + fnName + " {";
        // }
        // max characters should be
        let finalContext = "";
        if (i === 0) {
            finalContext = "→ ";
        }
        return finalContext + c.text.trim();
    })
}

/**
 * Reads the snippet from the source file. This does not follow any references
 * to other snippets (like in replace=other-snip-id)
 * @param snippet The snippet from snippets.json
 * @returns SnippetContent object with the snip content, context
 */
export async function readSnippet(
    snippet: z.infer<typeof snippetType>,
    beforeContext: number = 2,
    afterContext: number = 2): Promise<SnippetContent> {
    const text = await fs.readFile(snippet.filename, "utf-8");
    const lines = text.split("\n");
    let startSnipI = snippet.start_lineno - 1;
    let endSnipI = snippet.end_lineno - 1;
    let resSnipetText = lines.slice(startSnipI + 1, endSnipI).join("\n") + '\n';
    let resContextText = "a\nb\nc\n";
    const getBeforeContext = (startI: number,
        incrementDirection: number = -1,
        contextLength: number = SURROUNDING_CONTEXT_LINES
    ) => {
        let res = [];
        let taken = 0;
        for (let i = startI;
            taken < contextLength && i >= 0 && i < lines.length;
            i += incrementDirection
        ) {
            let line = lines[i];
            let trimmed = line.trimStart()
            if (trimmed.startsWith("//@s") || trimmed.startsWith("//-")) {
                // this is a snippet part, so skip this line
                continue;
            } else {
                res.push(line + "\n");
                taken++;
            }
        }
        if (incrementDirection === -1) {
            res.reverse();
        }
        res[res.length - 1] = res.at(-1)?.slice(0) ?? res.at(-1);
        return res.join("");
    }
    let surrounding = {
        before: getBeforeContext(startSnipI - 1, -1, beforeContext),
        after: getBeforeContext(endSnipI + 1, 1, (snippet.type === "end") ? 0 : afterContext),
    }

    let contextStack = [];
    for (const context of snippet.context_stack) {
        if (context.type === "NONE") continue;
        contextStack.push({
            text: lines[context.line - 1].trim(),
            type: context.type
        })
    }
    return {
        snippet: resSnipetText,
        contextStack,
        filename: getRelativeFilename(snippet),
        surrounding: {
            lines: SURROUNDING_CONTEXT_LINES,
            before: surrounding.before,
            after: surrounding.after,
        }
    }
}

export async function readSnippet1(snippet: z.infer<typeof snippetType>): Promise<SnippetContent> {
    const text = await fs.readFile(snippet.filename, "utf-8");
    let context_start = snippet.context_stack.at(-1)?.line ?? -1;
    let contextStarts: number[] = [];
    const contextTexts: string[] = [];
    for (const context of snippet.context_stack) {
        contextStarts.push(context.line - 1);
        contextTexts.push("");
    }

    context_start--; // so that when we subtract 1 on a newline,
    // 0 means we are at the context_start line.
    let start = snippet.start_lineno - 1;
    let end = snippet.end_lineno - 1;
    let snippetText = "";
    let contextText = "";
    let surrounding = {
        before: "",
        after: "",
    };
    for (let i = 0; i < text.length; i++) {
        for (let ci = 0; ci < contextStarts.length; ci++) {
            if (contextStarts[ci] === 0) {
                contextTexts[ci] += text[i];
            }
        }
        if (context_start === 0) {
            // we are in the context start line
            // context_start will become -1 after \n is hit
            contextText += text[i];
        }
        // get the starting surrounding context
        if (start <= SURROUNDING_CONTEXT_LINES && start > 0) {
            // this corresponds to the lines above the 
            // snippet start line
            surrounding.before += text[i];
        }
        if (start < 0) {
            // we are in the snippet
            if (text[i] === "\n") {
                end--;
            }
            if (end > 0) {
                // we are in the snippet
                snippetText += text[i];
            } else if (end >= -SURROUNDING_CONTEXT_LINES && end < 0) {
                // this corresponds to the lines after the 
                // snippet end line
                surrounding.after += text[i];
            }
        }
        else if (text[i] === "\n") {
            start--;
            end--;
            context_start--;
            for (let i = 0; i < contextStarts.length; i++) {
                contextStarts[i]--;
            }
        }
    }
    // console.log("All contexts are: ", contextTexts);
    const filename = getRelativeFilename(snippet);
    return {
        snippet: snippetText + "\n",
        // context: preProcessContexts(contextTexts.map((text, i) => ({
        //     text,
        //     type: snippet.context_stack[i].type
        // }))),
        contextStack: contextTexts.map((text, i) => ({
            text: text.trim(),
            type: snippet.context_stack[i].type,
        })),
        filename,
        surrounding: {
            lines: SURROUNDING_CONTEXT_LINES,
            before: surrounding.before,
            after: surrounding.after,
        }
    };
}

function getRelativeFilename(snippet: { id: string; start_lineno: number; end_lineno: number; filename: string; context_stack: { type: string; line: number; }[]; type: string; }) {
    return snippet.filename.substring(snippet.filename.indexOf(LLVM_ROOT_DIR_NAME)
        + LLVM_ROOT_DIR_NAME.length
        + 1
    );
}

