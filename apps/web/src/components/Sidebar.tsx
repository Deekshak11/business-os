import { useEffect } from "react";
import type { AppView } from "../lib/pipeline";

type Props = {
  view: AppView;
  onNavigate: (v: AppView) => void;
  onNewChat: () => void;
  systemsLive: boolean;
  stepLabel: string;
  outputCount?: number;
  /** Mobile drawer open state (controlled from App) */
  menuOpen: boolean;
  onMenuOpenChange: (open: boolean) => void;
};

const NAV: { id: AppView; label: string }[] = [
  { id: "chat", label: "Chat" },
  { id: "pipeline", label: "Pipeline" },
  { id: "plan", label: "Plan" },
  { id: "agents", label: "Agents" },
  { id: "outputs", label: "Outputs" },
];

export function Sidebar({
  view,
  onNavigate,
  onNewChat,
  systemsLive,
  stepLabel,
  outputCount = 0,
  menuOpen,
  onMenuOpenChange,
}: Props) {
  // Close drawer on Escape
  useEffect(() => {
    if (!menuOpen) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onMenuOpenChange(false);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [menuOpen, onMenuOpenChange]);

  // Lock body scroll when drawer open on mobile
  useEffect(() => {
    const prev = document.body.style.overflow;
    if (menuOpen) document.body.style.overflow = "hidden";
    else document.body.style.overflow = prev || "";
    return () => {
      document.body.style.overflow = prev || "";
    };
  }, [menuOpen]);

  function go(v: AppView) {
    onNavigate(v);
    onMenuOpenChange(false);
  }

  function newChat() {
    onNewChat();
    onMenuOpenChange(false);
  }

  return (
    <>
      {/* Mobile top bar */}
      <header className="mobile-topbar">
        <button
          type="button"
          className="menu-toggle"
          aria-label={menuOpen ? "Close menu" : "Open menu"}
          aria-expanded={menuOpen}
          onClick={() => onMenuOpenChange(!menuOpen)}
        >
          <span className={menuOpen ? "burger open" : "burger"} aria-hidden>
            <span />
            <span />
            <span />
          </span>
        </button>
        <div className="mobile-topbar-brand">
          <span className="brand-badge" aria-hidden>
            OS
          </span>
          <div>
            <div className="sidebar-title">Business OS</div>
            <div className="sidebar-sub">By Deekshak</div>
          </div>
        </div>
        <div className="mobile-topbar-status" title={systemsLive ? "Live" : "Offline"}>
          <span className={`status-dot ${systemsLive ? "" : "off"}`} />
        </div>
      </header>

      {/* Scrim behind drawer */}
      <button
        type="button"
        className={menuOpen ? "nav-scrim open" : "nav-scrim"}
        aria-label="Close menu"
        tabIndex={menuOpen ? 0 : -1}
        onClick={() => onMenuOpenChange(false)}
      />

      <aside className={menuOpen ? "sidebar open" : "sidebar"}>
        <div className="sidebar-brand desktop-only">
          <span className="brand-badge" aria-hidden>
            OS
          </span>
          <div>
            <div className="sidebar-title">Business OS</div>
            <div className="sidebar-sub">By Deekshak</div>
          </div>
        </div>

        <div className="sidebar-drawer-head mobile-only">
          <div className="sidebar-brand">
            <span className="brand-badge" aria-hidden>
              OS
            </span>
            <div>
              <div className="sidebar-title">Business OS</div>
              <div className="sidebar-sub">By Deekshak</div>
            </div>
          </div>
          <button
            type="button"
            className="drawer-close"
            aria-label="Close menu"
            onClick={() => onMenuOpenChange(false)}
          >
            ✕
          </button>
        </div>

        <button type="button" className="btn-new-chat" onClick={newChat}>
          <span className="plus">+</span> New chat
        </button>

        <nav className="sidebar-nav" aria-label="Main">
          {NAV.map((item) => (
            <button
              key={item.id}
              type="button"
              className={view === item.id ? "nav-item active" : "nav-item"}
              onClick={() => go(item.id)}
            >
              <span className="nav-label">
                {item.label}
                {item.id === "outputs" && outputCount > 0 ? (
                  <span className="nav-count">{outputCount}</span>
                ) : null}
              </span>
            </button>
          ))}
        </nav>

        <div className="sidebar-footer">
          <div className="status-block">
            <span className={`status-dot ${systemsLive ? "" : "off"}`} />
            <span>{systemsLive ? "All systems live" : "Systems offline"}</span>
          </div>
          <div className="step-chip">
            <span className="font-mono">Now</span> {stepLabel}
          </div>
        </div>
      </aside>
    </>
  );
}
