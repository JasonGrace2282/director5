/**
 * This is a minimal config.
 *
 * If you need the full config, get it from here:
 * https://unpkg.com/browse/tailwindcss@latest/stubs/defaultConfig.stub.js
 */

module.exports = {
	content: [
		/**
		 * HTML. Paths to Django template files that will contain Tailwind CSS classes.
		 */

		/*
		 * Main templates directory of the project (BASE_DIR/templates).
		 * Adjust the following line to match your project structure.
		 */
		"./manager/director/templates/**/*.html",
		"./manager/director/templates/*.html",

		/**
		 * JS: If you use Tailwind CSS in JavaScript, uncomment the following lines and make sure
		 * patterns match your project structure.
		 */
		/* JS 1: Ignore any JavaScript in node_modules folder. */
		// '!../../**/node_modules',
		/* JS 2: Process all JavaScript files in the project. */
		"./manager/director/static/**/*.js",
		"./manager/director/static/*.js",

		/**
		 * Python: If you use Tailwind CSS classes in Python, uncomment the following line
		 * and make sure the pattern below matches your project structure.
		 */
		// '../../**/*.py'
		"./manager/director/apps/**/*.py",
	],
	theme: {
		extend: {
			colors: {
				"dt-blue": "#087cfc",
			},
		},
		fontFamily: {
			sans: ["Inter", "sans-serif"],
		},
	},
	plugins: [
		/**
		 * '@tailwindcss/forms' is the forms plugin that provides a minimal styling
		 * for forms. If you don't like it or have own styling for forms,
		 * comment the line below to disable '@tailwindcss/forms'.
		 */
		require("@tailwindcss/forms"),
		require("@tailwindcss/typography"),
		require("@tailwindcss/aspect-ratio"),
	],
};
