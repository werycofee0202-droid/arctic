import { useEffect, useState } from "react";
import { getPartners } from "../api/partners";

const FALLBACK = [
  { id: "lensky",   img: "/partner_lensky.jpg",   name: "НП «Ленские столбы»",             href: "https://lena-pillars.ru/" },
  { id: "medvezhy", img: "/partner_medvezhy.jpg", name: "ГПЗ «Медвежьи острова»",          href: "#" },
  { id: "minobr",   img: "/partner_minobr.jpg",   name: "Минобразования регионов",         href: "#" },
  { id: "rgo",      img: "/partner_rgo.jpg",      name: "Русское географическое общество", href: "https://rgo.ru/" },
  { id: "ibpk",     img: "/partner_ibpk.jpg",     name: "ИБПК СО РАН",                     href: "#" },
];

export default function PartnersList() {
  const [items, setItems] = useState(FALLBACK);

  useEffect(() => {
    getPartners()
      .then((data) => { if (Array.isArray(data) && data.length) setItems(data); })
      .catch(() => {});
  }, []);

  return (
    <section className="partners" aria-label="Партнёры конкурса">
      <div className="wrap partners__inner">
        <span className="partners__label">Партнёры</span>
        <ul className="partners__list">
          {items.map((p) => (
            <li key={p.id}>
              <a
                className="partner"
                href={p.href}
                title={p.name}
                target={p.href?.startsWith("http") ? "_blank" : undefined}
                rel={p.href?.startsWith("http") ? "noopener noreferrer" : undefined}
              >
                <img src={p.img} alt={p.name} width={40} height={40} loading="lazy" />
                <span className="partner__name">{p.name}</span>
              </a>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}