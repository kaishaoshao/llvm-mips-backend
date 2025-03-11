// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

// https://astro.build/config
export default defineConfig({
	integrations: [
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
					label: 'Background',
					autogenerate: { directory: 'background' },
				},
				{
					label: "Section 1",
					autogenerate: {directory: "section 1"}
				},
				{
					label: 'Reference',
					autogenerate: { directory: 'reference' },
				},
				{
					label: '2. MIPS Architecture',
					autogenerate: { directory: 'mips-arch' },
				}
			],
		}),
	],
});
