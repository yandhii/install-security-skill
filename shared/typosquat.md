# Typosquat Detection

Use heuristic checks, not brute-force edit distance against a full list:

- Flag if the name differs from a highly popular package by 1 character (doubled letter, swap, omission): `expresss`, `loddash`, `axois`, `requets`
- Flag if it mimics an official scope but publisher differs: `@openai-tools/...` published by an unrelated account
- Flag if it adds common prefixes/suffixes to a popular name with a different maintainer: `node-lodash`, `py-requests`, `react-core-utils`
- If confidence is not high, mark as "suspicious — verify manually" rather than asserting typosquat
