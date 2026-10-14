import { useEffect, useState } from "react";

export default function SideDrawer({ children }) {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const onKey = (e) => e.key === "Escape" && setOpen(false);
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  useEffect(() => {
    document.body.style.overflow = open ? "hidden" : "";
    return () => { document.body.style.overflow = ""; };
  }, [open]);

  return (
    <>
      <button
        className="drawer-toggle"
        onClick={() => setOpen(true)}
        aria-label="Открыть меню разделов"
        type="button"
      >
        <span /><span /><span />
        <em>Разделы</em>
      </button>

      <div
        className={`drawer-backdrop ${open ? "is-open" : ""}`}
        onClick={() => setOpen(false)}
        aria-hidden={!open}
      />

      <aside
        className={`drawer ${open ? "is-open" : ""}`}
        role="dialog"
        aria-modal="true"
        aria-label="Навигация по разделам"
      >
        <div className="drawer__head">
          <span>Разделы</span>
          <button
            className="drawer__close"
            onClick={() => setOpen(false)}
            aria-label="Закрыть"
            type="button"
          >
            ×
          </button>
        </div>
        <div className="drawer__body">{children}</div>
      </aside>
    </>
  );
}