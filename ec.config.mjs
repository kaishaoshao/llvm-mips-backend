import { pluginCollapsibleSections } from '@expressive-code/plugin-collapsible-sections'
import { pluginCodeOutput } from './src/scripts/expressive-code.ts';
import { pluginCodeCaption } from './src/scripts/code-caption.ts';

/** @type {import('@astrojs/starlight/expressive-code').StarlightExpressiveCodeOptions} */
export default {
    plugins: [pluginCodeOutput(), pluginCodeCaption(), pluginCollapsibleSections()],
    themes: ['dark-plus', 'light-plus'],
    defaultProps: {
        wrap: true,
        overridesByLang: {
            'bash,sh': { preserveIndent: true}
        }
    },
    styleOverrides: {
        textMarkers: {
            backgroundOpacity: '20%',
            defaultChroma: '30',
            markBackground: '#22262d'
        }
    }
}
