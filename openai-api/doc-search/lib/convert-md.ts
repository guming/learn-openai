import * as fs from 'fs';
import { Content, Root } from 'mdast';
import { fromMarkdown } from 'mdast-util-from-markdown';
import { mdxFromMarkdown } from 'mdast-util-mdx';
import { toMarkdown } from 'mdast-util-to-markdown';
import { mdxjs } from 'micromark-extension-mdxjs';
import { u } from 'unist-builder';
import { filter } from 'unist-util-filter';

const markdownContent = fs.readFileSync('pages/docs/client-side-caching.md', 'utf-8');
const mdxTree = fromMarkdown(markdownContent, {
    extensions: [mdxjs()],
    mdastExtensions: [mdxFromMarkdown()],
})

function splitTreeBy(tree: Root, predicate: (node: Content) => boolean) {
    return tree.children.reduce<Root[]>((trees, node) => {
      const [lastTree] = trees.slice(-1)
  
      if (!lastTree || predicate(node)) {
        const tree: Root = u('root', [node])
        return trees.concat(tree)
      }
  
      lastTree.children.push(node)
      return trees
    }, [])
}

const mdTree = filter(
    mdxTree,
    (node) =>
      ![
        'mdxjsEsm',
        'mdxJsxFlowElement',
        'mdxJsxTextElement',
        'mdxFlowExpression',
        'mdxTextExpression',
      ].includes(node.type)
  )

if (!mdTree) {
    console.log(`md tree not found`)
}
const sectionTrees = splitTreeBy(mdTree, (node) => node.type === 'heading')

const sections = sectionTrees.map((tree) => {
    const [firstNode] = tree.children
    console.log(firstNode)
    const heading = firstNode.type === 'heading' ? firstNode.children[0].value : undefined

    return {
      content: toMarkdown(tree),
      heading,
      
    }
  })

console.log(sections)