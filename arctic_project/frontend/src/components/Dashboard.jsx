import { useEffect, useState } from "react";
import { getParticipantsCount } from "../api/stats";

export default function Dashboard() {
  const [count, setCount] = useState(0);

  useEffect(() => { getParticipantsCount().then(setCount); }, []);

  return (
    <div className="wrap">
      <h2>Дашборд</h2>
      <div className="counter">Участников: <b>{count}</b></div>
      {/* сюда позже: графики через recharts, геокарта и т.д. */}
    </div>
  );
}