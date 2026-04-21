import MarkdownIt from "markdown-it";
import katex from "katex";

const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
});

/**
 * Render Markdown string to HTML, with KaTeX math support.
 * Protects $...$ and $$...$$ blocks from Markdown processing,
 * then renders them with KaTeX after Markdown conversion.
 */
export function renderMarkdown(content: string): string {
  if (!content) return "";

  // Extract and protect block math ($$...$$)
  const blockMath: string[] = [];
  let processed = content.replace(/\$\$([\s\S]*?)\$\$/g, (_, math) => {
    blockMath.push(math);
    return `%%BLOCK${blockMath.length - 1}%%`;
  });

  // Extract and protect inline math ($...$)
  const inlineMath: string[] = [];
  processed = processed.replace(/\$([^\$\n]+?)\$/g, (_, math) => {
    inlineMath.push(math);
    return `%%INLINE${inlineMath.length - 1}%%`;
  });

  // Render Markdown
  let html = md.render(processed);

  // Restore block math with KaTeX
  html = html.replace(/%%BLOCK(\d+)%%/g, (_, idx) => {
    try {
      return katex.renderToString(blockMath[parseInt(idx)], {
        displayMode: true,
        throwOnError: false,
      });
    } catch {
      return `<pre class="text-red-500">${blockMath[parseInt(idx)]}</pre>`;
    }
  });

  // Restore inline math with KaTeX
  html = html.replace(/%%INLINE(\d+)%%/g, (_, idx) => {
    try {
      return katex.renderToString(inlineMath[parseInt(idx)], {
        throwOnError: false,
      });
    } catch {
      return `<code class="text-red-500">${inlineMath[parseInt(idx)]}</code>`;
    }
  });

  return html;
}
