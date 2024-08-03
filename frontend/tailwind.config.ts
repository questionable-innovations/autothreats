import type { Config } from 'tailwindcss';
import typegraphy from '@tailwindcss/typography';
import daisyui from 'daisyui';

export default {
	content: ['./src/**/*.{html,js,svelte,ts}'],

	theme: {
		extend: {}
	},

	plugins: [typegraphy, daisyui],

	daisyui: {
		logs: false
	}
} as Config;
