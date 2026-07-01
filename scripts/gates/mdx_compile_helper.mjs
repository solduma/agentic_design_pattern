#!/usr/bin/env node
// Helper: compile a single MDX file. Exit 0 on success, 1 on error.
import { compile } from '@mdx-js/mdx';
import { readFileSync } from 'fs';

const file = process.argv[2];
if (!file) {
  console.error('Usage: node mdx_compile_helper.mjs <file.mdx>');
  process.exit(1);
}

try {
  const content = readFileSync(file, 'utf8');
  await compile(content, { jsx: false });
  process.exit(0);
} catch (err) {
  console.error(`MDX compile error in ${file}:`);
  console.error(err.message);
  process.exit(1);
}
