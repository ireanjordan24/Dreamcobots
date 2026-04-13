'use strict';

module.exports = {
  env: {
    node: true,
    es2021: true,
    jest: true,
  },
  extends: ['eslint:recommended'],
  parserOptions: {
    ecmaVersion: 2021,
  },
  rules: {
    'no-console': 'off',
    'no-unused-vars': ['warn', { argsIgnorePattern: '^_' }],
    'no-var': 'error',
    'prefer-const': 'warn',
    eqeqeq: ['error', 'always'],
    curly: ['error', 'all'],
    semi: ['error', 'always'],
    quotes: ['error', 'single', { avoidEscape: true }],
  },
  ignorePatterns: ['node_modules/', 'coverage/', 'dist/', 'bots/', '*.py'],
  overrides: [
    {
      // Frontend React/JSX files and ESM config files
      files: [
        'dreamco-control-tower/frontend/**/*.js',
        'dreamco-control-tower/frontend/**/*.jsx',
        'dreamco-control-tower/frontend/**/*.ts',
        'dreamco-control-tower/frontend/**/*.tsx',
        'dreamco-control-tower/scripts/**/*.js',
        '*.jsx',
        '*.tsx',
      ],
      parserOptions: {
        sourceType: 'module',
        ecmaVersion: 2022,
        ecmaFeatures: { jsx: true },
      },
      env: {
        browser: true,
        node: true,
      },
      rules: {
        // PascalCase variables are React components used in JSX — suppress false
        // positives from ESLint's built-in no-unused-vars which doesn't track JSX usage.
        'no-unused-vars': ['warn', { argsIgnorePattern: '^_', varsIgnorePattern: '^[A-Z]' }],
      },
    },
  ],
};
