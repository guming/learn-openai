import * as fs from 'fs';
import MarkdownIt from 'markdown-it';

// 创建 markdown-it 实例
const md = new MarkdownIt();

// 要解析的 Markdown 文本
const markdownText = `
# Heading 1

This is some *italic* text.

- List item 1
- List item 2

[Link](https://www.example.com)

# Heading 2

This is some *italic* text.

- List item 3
- List item 4

[Link](https://www.example.com)
`;

// 解析 Markdown 文本为标记数组（解析树）
const tokens = md.parse(markdownText, {});

// 递归遍历解析树
function traverseTree(node) {
  if (Array.isArray(node)) {
    for (const childNode of node) {
      traverseTree(childNode);
    }
  } else if (typeof node === 'object' && node.type) {
    console.log('Type:', node.type, 'Content:', node.content);
    if (node.children) {
      traverseTree(node.children);
    }
  }
}

// 遍历解析树
traverseTree(tokens);




