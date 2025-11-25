import js from '@eslint/js';
import globals from 'globals';
import tseslint from 'typescript-eslint';
import prettierPlugin from 'eslint-plugin-prettier';

export default tseslint.config([
    {
        ignores: ['dist', 'bin', 'node_modules'],
    },
    {
        files: ['**/*.{ts,tsx}'],
        extends: [
            js.configs.recommended,
            ...tseslint.configs.recommended,
        ],
        languageOptions: {
            ecmaVersion: 2020,
            globals: globals.node,
        },
        plugins: {
            prettier: prettierPlugin,
        },
        rules: {
            // CLI-specific rules
            '@typescript-eslint/no-unused-vars': ['warn', { argsIgnorePattern: '^_' }],
            '@typescript-eslint/no-explicit-any': 'off',
            '@typescript-eslint/explicit-function-return-type': 'off',
            // Prettier integration
            'prettier/prettier': ['error', {
                singleQuote: true,
                semi: true,
                trailingComma: 'es5',
                printWidth: 100,
                tabWidth: 4,
                useTabs: false,
                arrowParens: 'always',
            }],
        },
    },
]);
