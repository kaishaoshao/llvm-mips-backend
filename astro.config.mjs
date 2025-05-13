// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import { exec } from "child_process";

import tailwindcss from '@tailwindcss/vite';

// https://astro.build/config
export default defineConfig({
    site: "https://optimisan.github.io/",
    integrations: [
        {
            name: "create-snippets-json",
            hooks: {
                'astro:config:setup': async (astroConfig) => {
                    // console.log('Running create-snippets-json');
                    exec("./build_snippets", (err, stdout, stderr) => {
                        if (err) {
                            astroConfig.logger.error(`Error running create-snippets-json: ${err}`);
                            return;
                        }
                        astroConfig.logger.info(`create-snippets-json: ${stdout}`);
                    })
                    astroConfig.logger.info('Running create-snippets-json');
                }
            }
        },
        starlight({
            title: 'LLVM to MIPS',
            customCss: ['./src/styles/custom.css'],
            social: {
                github: 'https://github.com/optimisan/llvm-mips-backend',
            },
            sidebar: [
                // {
                // 	label: 'Guides',
                // 	items: [
                // 		// Each item here is one entry in the navigation menu.
                // 		{ label: 'Example Guide', slug: 'guides/example' },
                // 	],
                // },
                {
                    label: 'About',
                    autogenerate: { directory: 'background' },
                },
                {
                    label: 'LLVM\'s CodeGen mechanics',
                    autogenerate: { directory: 'llvm-cg-ref' },
                    // slug: 'llvm-codegen-ref'
                },
                {
                    label: "A Minimal MIPS Backend",
                    autogenerate: { directory: "section 1" }
                },
                {
                    label: 'Reference',
                    autogenerate: { directory: 'reference' },
                },
            ],
        }),
    ],

    vite: {
        plugins: [tailwindcss()],
    },
});