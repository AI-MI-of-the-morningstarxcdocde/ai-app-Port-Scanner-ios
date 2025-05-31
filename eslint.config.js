export default [
  {
    ignores: ["**/*.py", "**/*.swift", "**/*.md", "**/*.json", "**/*.txt", "**/*.yml", "**/*.plist", "**/*.egg-info/**", "**/__pycache__/**"],
    files: ["**/*.js", "**/*.jsx", "**/*.ts", "**/*.tsx"],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: "module"
    },
    rules: {
      semi: ["error", "always"],
      quotes: ["error", "double"],
      "no-unused-vars": "warn"
    }
  }
];
