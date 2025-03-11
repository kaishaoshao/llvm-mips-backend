import type { Loader, LoaderContext} from "astro/loaders"
import {z} from "astro:content"

export function snippetLoader(options: {llvmRootPath: string}) : Loader {
    return {
        name: "snippets-loader",
        load: async(context: LoaderContext) : Promise<void> => {
            context.logger.debug("====calling a logger yo")
            console.log("==== running yuo")
            // context.store.set({
            //     id: "some entry",
            //     data: {
            //         snippetsInFile: ["aslkdjf", "aslkdjf"]
            //     }
            // })
        },
        schema: () => z.array(z.object({
            snippetId: z.string()
        }))
    }
}
