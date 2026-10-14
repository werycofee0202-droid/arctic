import { useEffect, useMemo, useRef, useState } from "react";
import {
  getProjectsByUser,
  createProject,
  updateProject,
  deleteProject,
  autoAssignExpert,
} from "../api/projects";
import { useAuth } from "../context/AuthContext";
import { validateFile, validateVideoLink } from "../utils/validateFile";

const NOMINATIONS = [
  "Экология Арктики",
  "Белый медведь и его охрана",
  "Климат и таяние льдов",
  "Северный морской путь",
  "Профессии в Арктике",
  "Свободная номинация",
];

const STATUS_LABEL = {
  draft:     "черновик",
  pending:   "на проверке",
  accepted:  "допущена",
  expertise: "на экспертизе",
  scored:    "оценена",
};

const EMPTY = {
  title: "",
  nomination: NOMINATIONS[0],
  annotation: "",
  videoUrl: "",
};

export default function Projects() {
  const { user } = useAuth();
  const [list, setList] = useState([]);
  const [form, setForm] = useState(EMPTY);
  const [files, setFiles] = useState({ project: null, presentation: null });
  const [errors, setErrors] = useState({});
  const [busy, setBusy] = useState(false);
  const [toast, setToast] = useState("");
  const [editingId, setEditingId] = useState(null);

  const projectInputRef = useRef(null);
  const presentationInputRef = useRef(null);

  const load = async () => {
    if (!user) return;
    try {
      const data = await getProjectsByUser(user.id);
      setList(Array.isArray(data) ? data : []);
    } catch {
      setList([]);
    }
  };

  useEffect(() => { load(); /* eslint-disable-next-line */ }, [user]);

  const setField = (k, v) => {
    setForm(f => ({ ...f, [k]: v }));
    setErrors(e => ({ ...e, [k]: null }));
  };

  const pickFile = (kind) => (e) => {
    const file = e.target.files?.[0] || null;
    const err = validateFile(file, kind);
    if (err) {
      setErrors(er => ({ ...er, [kind]: err }));
      setFiles(f => ({ ...f, [kind]: null }));
      return;
    }
    setErrors(er => ({ ...er, [kind]: null }));
    setFiles(f => ({ ...f, [kind]: file }));
  };

  const validate = () => {
    const e = {};
    if (form.title.trim().length < 5) e.title = "Минимум 5 символов";
    if (!form.nomination) e.nomination = "Выберите номинацию";
    if (form.annotation.trim().length < 30) e.annotation = "Минимум 30 символов";
    if (!files.project) e.project = "Прикрепите проект (PDF/DOCX)";
    if (!files.presentation) e.presentation = "Прикрепите презентацию (PDF/PPTX)";
    const vErr = validateVideoLink(form.videoUrl);
    if (vErr) e.videoUrl = vErr;
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const fileToBase64 = (file) =>
    new Promise((resolve, reject) => {
      const fr = new FileReader();
      fr.onload = () => resolve(fr.result);
      fr.onerror = reject;
      fr.readAsDataURL(file);
    });

  const reset = () => {
    setForm(EMPTY);
    setFiles({ project: null, presentation: null });
    setErrors({});
    setEditingId(null);
    if (projectInputRef.current) projectInputRef.current.value = "";
    if (presentationInputRef.current) presentationInputRef.current.value = "";
  };

  const submit = async (e) => {
    e.preventDefault();
    if (!validate()) return;
    setBusy(true);
    try {
      const payload = {
        ...form,
        userId: user.id,
        userName: user.name,
        school: user.school || "",
        region: user.region || "",
        status: "pending",
        createdAt: new Date().toISOString(),
        projectFile: {
          name: files.project.name,
          size: files.project.size,
          data: await fileToBase64(files.project),
        },
        presentationFile: {
          name: files.presentation.name,
          size: files.presentation.size,
          data: await fileToBase64(files.presentation),
        },
      };

      let saved;
      if (editingId) {
        saved = await updateProject(editingId, payload);
        setToast("Проект обновлён");
      } else {
        saved = await createProject(payload);
        setToast("Проект отправлен на проверку");
        autoAssignExpert(saved).catch(() => {});
      }

      reset();
      load();
    } catch (err) {
      setToast("Ошибка отправки. Проверьте соединение.");
    } finally {
      setBusy(false);
      setTimeout(() => setToast(""), 4000);
    }
  };

  const edit = (p) => {
    setEditingId(p.id);
    setForm({
      title: p.title,
      nomination: p.nomination,
      annotation: p.annotation || "",
      videoUrl: p.videoUrl || "",
    });
    setFiles({ project: null, presentation: null });
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const remove = async (id) => {
    if (!confirm("Удалить проект?")) return;
    try {
      await deleteProject(id);
      load();
    } catch {
      setToast("Не удалось удалить");
      setTimeout(() => setToast(""), 3000);
    }
  };

  const sorted = useMemo(
    () => [...list].sort((a, b) => (b.createdAt || "").localeCompare(a.createdAt || "")),
    [list]
  );

  if (!user) {
    return (
      <div className="wrap">
        <p className="muted">Войдите, чтобы подать проект.</p>
      </div>
    );
  }

  return (
    <div className="wrap projects">
      <h2>II этап — проектная работа</h2>
      <p className="muted">
        Заполните форму, прикрепите проект (PDF/DOCX) и презентацию (PDF/PPTX),
        при желании добавьте ссылку на видеоролик.
      </p>

      <form className="project-form" onSubmit={submit} noValidate>
        <div className={`field ${errors.title ? "has-error" : ""}`}>
          <label>Название проекта</label>
          <input
            value={form.title}
            onChange={(e) => setField("title", e.target.value)}
            placeholder="Например: Медвежьи острова — родильный дом белых медведей"
          />
          {errors.title && <div className="err">{errors.title}</div>}
        </div>

        <div className={`field ${errors.nomination ? "has-error" : ""}`}>
          <label>Номинация</label>
          <select
            value={form.nomination}
            onChange={(e) => setField("nomination", e.target.value)}
          >
            {NOMINATIONS.map(n => <option key={n}>{n}</option>)}
          </select>
          {errors.nomination && <div className="err">{errors.nomination}</div>}
        </div>

        <div className={`field full ${errors.annotation ? "has-error" : ""}`}>
          <label>Аннотация (30+ символов)</label>
          <textarea
            value={form.annotation}
            onChange={(e) => setField("annotation", e.target.value)}
            placeholder="Кратко: цель, методы, ожидаемый результат"
          />
          {errors.annotation && <div className="err">{errors.annotation}</div>}
        </div>

        <div className={`field ${errors.project ? "has-error" : ""}`}>
          <label>Файл проекта (PDF / DOCX, до 25 МБ)</label>
          <input
            ref={projectInputRef}
            type="file"
            accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            onChange={pickFile("project")}
          />
          {files.project && (
            <div className="file-meta">
              {files.project.name} • {(files.project.size / 1024 / 1024).toFixed(2)} МБ
            </div>
          )}
          {errors.project && <div className="err">{errors.project}</div>}
        </div>

        <div className={`field ${errors.presentation ? "has-error" : ""}`}>
          <label>Презентация (PDF / PPTX, до 25 МБ)</label>
          <input
            ref={presentationInputRef}
            type="file"
            accept=".pdf,.pptx,application/pdf,application/vnd.openxmlformats-officedocument.presentationml.presentation"
            onChange={pickFile("presentation")}
          />
          {files.presentation && (
            <div className="file-meta">
              {files.presentation.name} • {(files.presentation.size / 1024 / 1024).toFixed(2)} МБ
            </div>
          )}
          {errors.presentation && <div className="err">{errors.presentation}</div>}
        </div>

        <div className={`field full ${errors.videoUrl ? "has-error" : ""}`}>
          <label>Ссылка на видеоролик (необязательно)</label>
          <input
            value={form.videoUrl}
            onChange={(e) => setField("videoUrl", e.target.value)}
            placeholder="https://..."
          />
          {errors.videoUrl && <div className="err">{errors.videoUrl}</div>}
        </div>

        <div className="form-actions full">
          <button className="btn btn--primary" type="submit" disabled={busy}>
            {busy ? "Отправка…" : editingId ? "Сохранить изменения" : "Отправить проект"}
          </button>
          {editingId && (
            <button type="button" className="btn btn--ghost" onClick={reset}>
              Отмена
            </button>
          )}
          <span className="form-note">
            Отправляя, вы подтверждаете согласие на обработку ПД (152-ФЗ).
          </span>
        </div>
      </form>

      {toast && <div className="toast">{toast}</div>}

      <h3 className="projects__title">Мои работы</h3>
      {sorted.length === 0 && <p className="muted">Пока нет проектов.</p>}

      <div className="projects__list">
        {sorted.map(p => (
          <article key={p.id} className="project-card">
            <div className="project-card__head">
              <span className={`status status--${p.status}`}>
                {STATUS_LABEL[p.status] || p.status}
              </span>
              <span className="muted">
                {p.createdAt ? new Date(p.createdAt).toLocaleString("ru-RU") : ""}
              </span>
            </div>
            <h4>{p.title}</h4>
            <p className="muted">{p.nomination}</p>
            {p.annotation && <p className="project-card__ann">{p.annotation}</p>}

            {p.scores && (
              <div className="project-card__score">
                Оценка эксперта: <b>{p.finalScore ?? "—"}</b>
              </div>
            )}
            {p.expertComment && (
              <div className="project-card__comment">«{p.expertComment}»</div>
            )}

            {(p.status === "draft" || p.status === "pending") && (
              <div className="project-card__actions">
                <button className="btn btn--ghost" onClick={() => edit(p)}>
                  Редактировать
                </button>
                <button className="btn btn--ghost danger" onClick={() => remove(p.id)}>
                  Удалить
                </button>
              </div>
            )}
          </article>
        ))}
      </div>
    </div>
  );
}