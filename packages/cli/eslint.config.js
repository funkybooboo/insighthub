import js from '@eslint/js';
import globals from 'globals';
import tsPlugin from '@typescript-eslint/eslint-plugin';
import tsParserPkg from '@typescript-eslint/parser';
import prettierPlugin from 'eslint-plugin-prettier';
import { globalIgnores } from 'eslint/config';

const { default: tsParser } = tsParserPkg;

export default [
  // Ignore build folders
  globalIgnores(['dist', 'coverage']),

  // JS recommended rules (flat-config compatible)
  js.configs.recommended,

  // TypeScript + Prettier config
  {
    files: ['**/*.{ts,tsx}'],
    languageOptions: {
      parser: tsParser,
      ecmaVersion: 2020,
      globals: globals.browser,
    },
    plugins: {
      '@typescript-eslint': tsPlugin,
      prettier: prettierPlugin,
    },
    rules: {
      // TypeScript rules
      '@typescript-eslint/no-unused-vars': ['warn', { argsIgnorePattern: '^_' }],
      '@typescript-eslint/no-explicit-any': 'off',
      // Prettier rules
      'prettier/prettier': ['error', { singleQuote: true, semi: true, trailingComma: 'all', printWidth: 100 }],
    },
  },
];
