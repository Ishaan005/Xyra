import { dirname } from "path";
import { fileURLToPath } from "url";
import { FlatCompat } from "@eslint/eslintrc";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const compat = new FlatCompat({
  baseDirectory: __dirname,
});

const eslintConfig = [
  ...compat.extends("next/core-web-vitals", "next/typescript"),
  {
    ignores: [
      "**/dist/**",
      "**/node_modules/**",
      "**/.next/**",
      "**/build/**",
      "**/*.js", // Ignore compiled JS files
      "**/components/dist/**",
      "**/components/ui/dist/**",
      "**/components/layout/dist/**",
      "**/lib/dist/**"
    ]
  },
  {
    rules: {
      "@typescript-eslint/no-explicit-any": "warn", // Change to warning instead of error for development
      "react/no-unescaped-entities": "off", // Disable this rule for development
      "@typescript-eslint/no-unused-vars": "warn", // Warning instead of error
      "@typescript-eslint/no-require-imports": "error",
      "@typescript-eslint/no-empty-object-type": "warn", // Warning for empty interfaces
      "react-hooks/exhaustive-deps": "warn" // Warning for hook dependencies
    }
  }
];

export default eslintConfig;
