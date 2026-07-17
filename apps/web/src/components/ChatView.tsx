import { FormEvent, RefObject, useEffect, useRef } from "react";
import { Markdown } from "./Markdown";
import { PageHeader } from "./PageHeader";

export type UiMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
};

type Props = {
  messages: UiMessage[];
  busy: boolean;
  input: string;
  setInput: (v: string) => void;
  onSubmit: (e?: FormEvent) => void;
  systemsLive: boolean;
  error: string | null;
  logRef: RefObject<HTMLDivElement | null>;
};

export function ChatView({
  messages,
  busy,
  input,
  setInput,
  onSubmit,
  systemsLive,
  error,
  logRef,
}: Props) {
  const taRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    const el = taRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 160)}px`;
  }, [input]);

  return (
    <div className="view chat-view">
      <PageHeader
        title={
          <>
            Business{" "}
            <em className="font-display text-gradient">strategist</em>
          </>
        }
        description="Trained on Alex Hormozi's $100M frameworks"
      />

      {error && <div className="error-banner">{error}</div>}

      <div className="chat-scroll" ref={logRef}>
        <div className="chat-inner page-rail">
          {messages.map((m) => (
            <div
              key={m.id}
              className={
                m.role === "user" ? "bubble-row user" : "bubble-row assistant"
              }
            >
              <div
                className={m.role === "user" ? "bubble user" : "bubble assistant"}
              >
                {m.role === "assistant" ? (
                  <Markdown content={m.content} />
                ) : (
                  <div className="md-body plain">{m.content}</div>
                )}
              </div>
            </div>
          ))}
          {busy && (
            <div className="bubble-row assistant">
              <div className="bubble assistant typing">
                <span className="spinner" />
                <span>Thinking…</span>
              </div>
            </div>
          )}
        </div>
      </div>

      <form className="composer-dock" onSubmit={onSubmit}>
        <div className="composer-box glass">
          <textarea
            ref={taRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={
              systemsLive
                ? "Message the strategist…"
                : "Systems offline — check the backend…"
            }
            rows={1}
            disabled={busy || !systemsLive}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                onSubmit();
              }
            }}
          />
          <div className="composer-actions">
            <button
              type="submit"
              className="btn btn-primary btn-focus"
              disabled={busy || !systemsLive || !input.trim()}
            >
              {busy ? "…" : "Send"}
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}
