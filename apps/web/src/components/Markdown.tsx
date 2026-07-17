import { markdownToHtml } from "../lib/markdown";

type Props = {
  content: string;
  className?: string;
};

export function Markdown({ content, className }: Props) {
  const html = markdownToHtml(content);
  return (
    <div
      className={className ? `md-body ${className}` : "md-body"}
      dangerouslySetInnerHTML={{ __html: html }}
    />
  );
}
