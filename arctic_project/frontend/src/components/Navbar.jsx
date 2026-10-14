import { useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import AuthModal from "./AuthModal";

export default function Navbar() {
  const { user, logout } = useAuth();
  const [open, setOpen] = useState(false);

  return (
    <header className="topbar">
      <div className="wrap topbar__inner">
        <Link to="/" className="logo">
          <span className="logo__mark" />
          <span className="logo__text">
            Удивительная Арктика
            <small>конкурс • 2021—2026</small>
          </span>
        </Link>

        <nav className="nav">
          <Link to="/">О конкурсе</Link>
          <Link to="/tests">Тестирование</Link>
          <Link to="/projects">Проекты</Link>
          <Link to="/dashboard">Кабинет</Link>
        </nav>

        <div className="lang">
          {user ? (
            <>
              <span style={{ color: "var(--muted)", fontSize: 13 }}>
                {user.name} · {user.role}
              </span>
              <button onClick={logout}>Выйти</button>
            </>
          ) : (
            <button onClick={() => setOpen(true)}>Войти</button>
          )}
        </div>
      </div>

      <AuthModal open={open} onClose={() => setOpen(false)} />
    </header>
  );
}