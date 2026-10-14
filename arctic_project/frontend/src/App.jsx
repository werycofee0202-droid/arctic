import { useEffect } from "react";
import { Routes, Route, Link } from "react-router-dom";
import Navbar from "./components/Navbar";
import PartnersList from "./components/PartnersList";
import SideDrawer from "./components/SideDrawer";
import Tests from "./components/Tests";
import Projects from "./components/Projects";
import Experts from "./components/Experts";
import Dashboard from "./components/Dashboard";
import "./App.css";

/* ================== ГЛАВНАЯ ================== */
function Home() {
  useEffect(() => {
    const el = document.getElementById("participantsCounter");
    if (!el) return;

    const target = 10248;
    const duration = 1400;
    let start = null;
    let raf;

    const easeOut = (t) => 1 - Math.pow(1 - t, 3);

    const step = (ts) => {
      if (!start) start = ts;
      const p = Math.min((ts - start) / duration, 1);
      const val = Math.round(easeOut(p) * target);
      el.textContent = val.toLocaleString("ru-RU");
      if (p < 1) raf = requestAnimationFrame(step);
    };

    raf = requestAnimationFrame(step);
    return () => cancelAnimationFrame(raf);
  }, []);

  return (
    <section className="hero">
      <div className="wrap hero__inner">
        <nav className="breadcrumbs" aria-label="Хлебные крошки">
          <Link to="/">Главная</Link>
          <span className="sep">/</span>
          <span>Конкурс</span>
        </nav>

        <h1>
          Удивительная и <span className="grad">неизведанная Арктика</span>
        </h1>
        <p className="lead">
          Информационно-просветительский конкурс для школьников из 30+ регионов.
          Пройдите тестирование I этапа — и получите электронный сертификат с QR-кодом.
        </p>

        <div className="aurora-window" aria-hidden="true">
          <div className="aurora-window__glow" />
          <div className="aurora-window__stars" />
          <div className="aurora-window__ribbon" />
        </div>

        <div className="hero-actions">
          <Link className="btn btn--primary btn--lg" to="/tests">
            Пройти тестирование
          </Link>
          <Link className="btn btn--ghost" to="/projects">
            Подать проект
          </Link>
          <a className="btn btn--ghost" href="#videos">
            Смотреть видеоролики
          </a>
        </div>

        <div className="counter" aria-live="polite">
          <span className="dot" aria-hidden="true" />
          <span>Участников уже:</span>
          <b id="participantsCounter">0</b>
          <span className="muted">из 30+ регионов</span>
        </div>
      </div>
    </section>
  );
}

/* ================== КОРЕНЬ ================== */
export default function App() {
  return (
    <>
      <div className="aurora-bg" aria-hidden="true" />

      <Navbar />
      <PartnersList />

      <SideDrawer>
        <h3>Исследовать</h3>
        <nav>
          <a href="#">Наука заповедного дела</a>
          <a href="#" className="is-active">Нормативные документы</a>
          <a href="#">Приоритеты заповедной науки</a>
          <a href="#">Научные публикации</a>
          <a href="#">Научные мероприятия</a>
        </nav>

        <div className="side-divider" />

        <h3>Участникам</h3>
        <nav>
          <Link to="/tests">Пройти тестирование</Link>
          <Link to="/projects">Подать проект</Link>
          <a href="#">Требования к работам</a>
          <a href="#">Критерии оценки</a>
          <a href="#">Шаблоны документов</a>
          <a href="#">FAQ</a>
        </nav>

        <div className="side-divider" />

        <h3>Кабинеты</h3>
        <nav>
          <Link to="/dashboard">Личный кабинет</Link>
          <Link to="/experts">Кабинет эксперта</Link>
        </nav>
      </SideDrawer>

      <main className="layout">
        <Routes>
          <Route path="/"          element={<Home />} />
          <Route path="/tests"     element={<Tests />} />
          <Route path="/projects"  element={<Projects />} />
          <Route path="/experts"   element={<Experts />} />
          <Route path="/dashboard" element={<Dashboard />} />
        </Routes>
      </main>

      <footer>
        <div className="wrap">
          <div className="foot-grid">
            <div>
              <div className="logo" style={{ marginBottom: 14 }}>
                <span className="logo__mark" aria-hidden="true" />
                <span className="logo__text">
                  Удивительная Арктика
                  <small>информационно-просветительский конкурс</small>
                </span>
              </div>
              <p className="foot-about">
                Конкурс для школьников из 30+ регионов России. Изучаем Арктику,
                белого медведя и Медвежьи острова — вместе с НП «Ленские столбы»,
                ГПЗ «Медвежьи острова», ИБПК СО РАН и РГО.
              </p>
            </div>

            <div>
              <h4>Конкурс</h4>
              <a href="#">О конкурсе</a>
              <a href="#">Номинации и этапы</a>
              <a href="#">Призы и награды</a>
              <a href="#">История 2021—2023</a>
            </div>

            <div>
              <h4>Участникам</h4>
              <Link to="/tests">Пройти тестирование</Link>
              <Link to="/projects">Подать проект</Link>
              <a href="#">Требования к работам</a>
              <a href="#">Шаблоны документов</a>
            </div>

            <div>
              <h4>Контакты</h4>
              <a href="mailto:org@arctic-contest.ru">org@arctic-contest.ru</a>
              <a href="tel:+70000000000">+7 (000) 000-00-00</a>
              <div className="socials" style={{ marginTop: 12 }}>
                <a href="#" aria-label="ВКонтакте">VK</a>
                <a href="#" aria-label="Telegram">TG</a>
              </div>
            </div>
          </div>

          <div className="foot-bottom">
            <span>© 2021—2026 Конкурс «Удивительная и неизведанная Арктика».</span>
            <span>Положение • Политика конфиденциальности • 152-ФЗ</span>
          </div>
        </div>
      </footer>
    </>
  );
}