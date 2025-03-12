import { z } from "astro:content";
import fs from "node:fs/promises"

const SURROUNDING_CONTEXT_LINES = 2;

export const snippetType = z.object({
    id: z.string(),
    start_lineno: z.number(),
    end_lineno: z.number(),
    filename: z.string(),
    context_stack: z.array(z.object({
        line: z.number(),
        type: z.string(),
    }))
})

export async function readSnippet(snippet: z.infer<typeof snippetType>) {
    const text = await fs.readFile(snippet.filename, "utf-8");
    let context_start = snippet.context_stack.at(-1)?.line ?? -1;
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
        }
    }
    return {
        snippet: snippetText + "\n",
        context: contextText,
        filename: snippet.filename,
        surrounding: {
            lines: SURROUNDING_CONTEXT_LINES,
            before: surrounding.before,
            after: surrounding.after
        }
    };
}
