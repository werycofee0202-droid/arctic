import { useEffect, useMemo, useState } from "react";
import { getProjectsByExpert, updateProject, calcFinalScore } from "../api/projects";
import { useAuth } from "../context/AuthContext";

// Критерии и коэффициенты значимости (из Положения)
export const CRITERIA = [
  { key: "relevance", label: "Актуальность",             weight: 1.2 },
  { key: "novelty",   label: "Новизна",                  weight: 1.0 },
  { key: "depth",     label: "Глубина исследования",     weight: 1.3 },
  { key: "practical", label: "Практическая значимость",  weight: 1.1 },
  { key: "design",    label: "Оформление и презентация", weight: 0.9 },
  { key: "defense",   label: "Защита (ВКС)",             weight: 1.0 },
];

const WEIGHTS = CRITERIA.reduce((a, c) => ({ ...a, [c.key]: c.weight }), {});

export default function Experts() {
  const { user } = useAuth();
  const [works, setWorks] = useState([]);
  const [openId, setOpenId] = useState(null);

  useEffect(() => {
    if (user?.role !== "expert") return;
    getProjectsByExpert(user.id).then(setWorks);
  }, [user]);

  const scored = useMemo(
    () => works.filter(w => w.status === "scored").length,
    [works]
  );

  if (user?.role !== "expert") {
    return (
      <div className="wrap">
        <h2>Кабинет эксперта</h2>
        <p className="muted">Доступ только для пользователей с ролью «эксперт».</p>
      </div>
    );
  }

  const saveScore = async (project, scores, comment) => {
    const finalScore = calcFinalScore(scores, WEIGHTS);
    const updated = await updateProject(project.id, {
      scores,
      finalScore,
      expertComment: comment || "",
      status: "scored",
      scoredAt: new Date().toISOString(),
    });
    setWorks(list => list.map(w => (w.id === project.id ? updated : w)));
    setOpenId(null);
  };

  return (
    <div className="wrap experts">
      <div className="experts__head">
        <h2>Работы на экспертизе</h2>
        <div className="muted">
          Всего: <b>{works.length}</b> • оценено: <b>{scored}</b>
        </div>
      </div>

      {works.length === 0 && <p className="muted">Пока нет назначенных работ.</p>}

      <div className="experts__list">
        {works.map(p => (
          <article key={p.id} className="project-card">
            <div className="project-card__head">
              <span className={`status status--${p.status}`}>
                {p.status === "scored" ? "оценена" : "на экспертизе"}
              </span>
              <span className="muted">{p.region} • {p.school}</span>
            </div>
            <h4>{p.title}</h4>
            <p className="muted">{p.nomination} • автор: {p.userName}</p>
            <p className="project-card__ann">{p.annotation}</p>

            {p.projectFile && (
              <a className="link" href={p.projectFile.data} download={p.projectFile.name}>
                Скачать проект ({p.projectFile.name})
              </a>
            )}
            {p.presentationFile && (
              <a className="link" href={p.presentationFile.data} download={p.presentationFile.name}>
                Скачать презентацию ({p.presentationFile.name})
              </a>
            )}
            {p.videoUrl && (
              <a className="link" href={p.videoUrl} target="_blank" rel="noreferrer">
                Видеоролик
              </a>
            )}

            {p.status === "scored" ? (
              <div className="project-card__score">
                Итог: <b>{p.finalScore}</b>
                {p.expertComment && (
                  <div className="project-card__comment">«{p.expertComment}»</div>
                )}
              </div>
            ) : openId === p.id ? (
              <ScoreForm
                onCancel={() => setOpenId(null)}
                onSave={(scores, comment) => saveScore(p, scores, comment)}
              />
            ) : (
              <button className="btn btn--primary" onClick={() => setOpenId(p.id)}>
                Оценить
              </button>
            )}
          </article>
        ))}
      </div>
    </div>
  );
}

function ScoreForm({ onCancel, onSave }) {
  const [scores, setScores] = useState(
    CRITERIA.reduce((a, c) => ({ ...a, [c.key]: 0 }), {})
  );
  const [comment, setComment] = useState("");

  const set = (k, v) => setScores(s => ({ ...s, [k]: Number(v) }));
  const preview = calcFinalScore(scores, WEIGHTS);

  return (
    <div className="score-form">
      {CRITERIA.map(c => (
        <div key={c.key} className="score-row">
          <label>
            {c.label} <span className="muted">×{c.weight}</span>
          </label>
          <input
            type="range"
            min="0"
            max="100"
            step="1"
            value={scores[c.key]}
            onChange={(e) => set(c.key, e.target.value)}
          />
          <span className="score-val">{scores[c.key]}</span>
        </div>
      ))}

      <textarea
        placeholder="Комментарий и рекомендации"
        value={comment}
        onChange={(e) => setComment(e.target.value)}
      />

      <div className="score-form__actions">
        <div className="muted">
          Итоговый балл: <b>{preview}</b>
        </div>
        <button className="btn btn--ghost" onClick={onCancel} type="button">
          Отмена
        </button>
        <button
          className="btn btn--primary"
          type="button"
          onClick={() => onSave(scores, comment)}
        >
          Сохранить оценку
        </button>
      </div>
    </div>
  );
}