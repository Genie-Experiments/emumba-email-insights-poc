import React from "react";
import ReactMarkdown from "react-markdown";

interface MarkdownMarkupRendererProps {
  content: string;
}

const MarkdownMarkupRenderer: React.FC<MarkdownMarkupRendererProps> = ({
  content,
}) => {
  // Pre-process content to handle mixed Markdown and HTML
  const processContent = (text: string) => {
    // Split content into Markdown and HTML parts
    const parts = text.split(/(\<[^>]*\>)/g);
    return parts.map((part, index) => {
      // If part contains HTML tags, render as raw HTML
      if (/<[^>]*>/.test(part)) {
        return <span key={index} dangerouslySetInnerHTML={{ __html: part }} />;
      }

      // Otherwise, treat it as Markdown
      return <ReactMarkdown key={index}>{part}</ReactMarkdown>;
    });
  };

  return <p>{processContent(content)}</p>;
};

export default MarkdownMarkupRenderer;
