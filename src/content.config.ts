import { defineCollection , z} from 'astro:content';
import { docsLoader } from '@astrojs/starlight/loaders';
import { docsSchema } from '@astrojs/starlight/schema';
import { snippetLoader } from './scripts/snippets-loader';
import { file } from 'astro/loaders';
import { snippetType } from './util/read-snippet';

const snippets1 = defineCollection({
    loader: async () =>  {
        const response = await fetch("https://restcountries.com/v3.1/all")
        const data = await response.json();
		console.log("========running running ===========")
        return data.map(country => {
            return {
                id: country.cca3,
                ...country
            }
        })
    }
})

export const collections = {
	docs: defineCollection({ loader: docsLoader(), schema: docsSchema() }),
    snippets: defineCollection({
        loader: file("snippets.json"),
        schema: snippetType
    })
	// snippets: snippetLoader({
	// 	llvmRootPath: "something here"
	// }),	
	// something: snippets
};

