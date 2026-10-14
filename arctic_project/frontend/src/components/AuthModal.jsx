import { useState } from "react";
import { useAuth } from "../context/AuthContext";

export default function AuthModal({ open, onClose }) {
  const { login, register } = useAuth();
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({ email: "", password: "", name: "", role: "participant" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  if (!open) return null;

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      if (mode === "login") await login({ email: form.email, password: form.password });
      else await register(form);
      onClose();
    } catch (err) {
      setError(err.response?.data?.message || "Ошибка. Проверьте данные.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <form className="modal" onClick={(e) => e.stopPropagation()} onSubmit={submit}>
        <h3>{mode === "login" ? "Вход" : "Регистрация"}</h3>

        {mode === "register" && (
          <input placeholder="Имя" value={form.name}
                 onChange={(e) => setForm({ ...form, name: e.target.value })} required />
        )}
        <input type="email" placeholder="E-mail" value={form.email}
               onChange={(e) => setForm({ ...form, email: e.target.value })} required />
        <input type="password" placeholder="Пароль" value={form.password}
               onChange={(e) => setForm({ ...form, password: e.target.value })} required />

        {mode === "register" && (
          <select value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })}>
            <option value="participant">Участник</option>
            <option value="teacher">Руководитель</option>
            <option value="expert">Эксперт</option>
          </select>
        )}

        {error && <div className="err">{error}</div>}

        <button type="submit" disabled={loading}>
          {loading ? "…" : mode === "login" ? "Войти" : "Создать аккаунт"}
        </button>

        <button type="button" onClick={() => setMode(mode === "login" ? "register" : "login")}>
          {mode === "login" ? "Нет аккаунта? Регистрация" : "Уже есть аккаунт? Войти"}
        </button>
      </form>
    </div>
  );
}