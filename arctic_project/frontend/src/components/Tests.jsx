import { useEffect, useMemo, useRef, useState } from "react";
import { getTest, saveTestResult, saveCertificate } from "../api/tests";
import { useAuth } from "../context/AuthContext";
import { generateCertificate, makeCertId } from "../utils/certificate";

const LETTERS = ["A", "B", "C", "D"];

function shuffle(arr) {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

export default function Tests() {
  const { user } = useAuth();

  const [test, setTest] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({});
  const [current, setCurrent] = useState(0);
  const [secondsLeft, setSecondsLeft] = useState(0);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const timerRef = useRef(null);

  useEffect(() => {
    getTest(1)
      .then((data) => {
        setTest(data);
        const shuffled = shuffle(data.questions).slice(0, data.questionsCount || 10);
        setQuestions(shuffled);
        setSecondsLeft(data.timeLimitSec || 900);
      })
      .catch(() => setError("Тест временно недоступен."))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (!questions.length || result) return;
    timerRef.current = setInterval(() => {
      setSecondsLeft((s) => {
        if (s <= 1) {
          clearInterval(timerRef.current);
          finish();
          return 0;
        }
        return s - 1;
      });
    }, 1000);
    return () => clearInterval(timerRef.current);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [questions, result]);

  const picked = useMemo(() => Object.keys(answers).length, [answers]);

  const choose = (qid, idx) => {
    setAnswers((a) => ({ ...a, [qid]: idx }));
  };

  const finish = async () => {
    if (busy) return;
    setBusy(true);
    clearInterval(timerRef.current);

    let correct = 0;
    questions.forEach((q) => {
      if (answers[q.id] === q.correct) correct++;
    });

    const score = correct;
    const total = questions.length;
    const passed = total ? score / total >= 0.6 : false;
    const certId = makeCertId();

    const payload = {
      userId: user?.id || null,
      userName: user?.name || "Участник",
      testId: test?.id || 1,
      answers,
      score,
      total,
      passed,
      certId,
      createdAt: new Date().toISOString(),
    };

    try {
      await saveTestResult(payload);
      await saveCertificate({
        id: certId,
        userName: payload.userName,
        score,
        total,
        createdAt: payload.createdAt,
      });
    } catch {
      // не блокируем показ результата
    }

    setResult({ score, total, passed, certId });
    setBusy(false);
  };

  const download = async () => {
    await generateCertificate({
      participantName: user?.name || "Участник",
      region: user?.region || "Регион не указан",
      school: user?.school || "Школа не указана",
      score: result.score,
      total: result.total,
      certId: result.certId,
    });
  };

  const mmss = (s) => {
    const m = Math.floor(s / 60).toString().padStart(2, "0");
    const ss = (s % 60).toString().padStart(2, "0");
    return `${m}:${ss}`;
  };

  if (loading) return <div className="wrap">Загрузка теста…</div>;
  if (error)   return <div className="wrap err">{error}</div>;

  if (result) {
    return (
      <div className="wrap test-result">
        <h2>{result.passed ? "Поздравляем, вы прошли I этап!" : "Тест завершён"}</h2>
        <p className="lead">
          Результат: <b>{result.score}</b> из <b>{result.total}</b>.
          {result.passed
            ? " Вы допущены ко II этапу — загрузке проекта."
            : " Попробуйте ещё раз — порог 60%."}
        </p>
        <p className="muted">
          Номер сертификата: <b>{result.certId}</b>
        </p>

        <div className="hero-actions">
          <button className="btn btn--primary" onClick={download}>
            Скачать сертификат PDF
          </button>
          <button className="btn btn--ghost" onClick={() => window.location.reload()}>
            Пройти заново
          </button>
        </div>
      </div>
    );
  }

  const q = questions[current];
  const total = questions.length;

  return (
    <div className="wrap test">
      <div className="test__head">
        <div>
          <h2>{test?.title}</h2>
          <p className="muted">
            Вопрос {current + 1} из {total} • отвечено: {picked}
          </p>
        </div>
        <div className={`timer ${secondsLeft < 60 ? "timer--danger" : ""}`}>
          ⏱ {mmss(secondsLeft)}
        </div>
      </div>

      <div className="progress">
        <div
          className="progress__bar"
          style={{ width: `${((current + 1) / total) * 100}%` }}
        />
      </div>

      <div className="question">
        <p className="question__text">{q.text}</p>
        <div className="options">
          {q.options.map((opt, idx) => {
            const active = answers[q.id] === idx;
            return (
              <button
                key={idx}
                className={`option ${active ? "is-active" : ""}`}
                onClick={() => choose(q.id, idx)}
                type="button"
              >
                <span className="option__letter">{LETTERS[idx]}</span>
                <span>{opt}</span>
              </button>
            );
          })}
        </div>
      </div>

      <div className="test__nav">
        <button
          className="btn btn--ghost"
          disabled={current === 0}
          onClick={() => setCurrent((c) => c - 1)}
        >
          Назад
        </button>

        {current < total - 1 ? (
          <button
            className="btn btn--primary"
            disabled={answers[q.id] === undefined}
            onClick={() => setCurrent((c) => c + 1)}
          >
            Далее
          </button>
        ) : (
          <button
            className="btn btn--primary"
            disabled={busy || picked < total}
            onClick={finish}
          >
            {busy ? "Отправка…" : "Завершить тест"}
          </button>
        )}
      </div>
    </div>
  );
}