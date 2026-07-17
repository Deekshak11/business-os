import { ReactNode } from "react";

type Props = {
  title: ReactNode;
  description: string;
  actions?: ReactNode;
};

/**
 * Shared product chrome for every main view (Chat, Pipeline, Plan, Agents).
 * Always top-left — same title metrics, same subtitle, same spacing.
 */
export function PageHeader({ title, description, actions }: Props) {
  return (
    <header className="page-header">
      <div className="page-header-copy">
        <p className="page-kicker">
          <span className="dot" aria-hidden />
          Business OS
        </p>
        <h1 className="page-title">{title}</h1>
        <p className="page-desc">{description}</p>
      </div>
      {actions ? <div className="page-header-actions">{actions}</div> : null}
    </header>
  );
}
