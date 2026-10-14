import api from "./client";

// ---------- CRUD ----------
export const getProjects = () =>
  api.get("/projects/").then((r) => r.data);

export const getProject = (id) =>
  api.get(`/projects/${id}`).then((r) => r.data);

export const createProject = (data) =>
  api.post("/projects/", data).then((r) => r.data);

export const updateProject = (id, data) =>
  api.patch(`/projects/${id}`, data).then((r) => r.data);

export const deleteProject = (id) =>
  api.delete(`/projects/${id}`).then((r) => r.data);

// ---------- Фильтры (query-параметры FastAPI) ----------
export const getProjectsByUser = (userId) =>
  api.get("/projects/", { params: { user_id: userId } }).then((r) => r.data);

export const getProjectsByExpert = (expertId) =>
  api.get("/projects/", { params: { expert_id: expertId } }).then((r) => r.data);

// ---------- Авто-распределение по эксперту ----------
export const autoAssignExpert = async (project) => {
  const [experts, projects] = await Promise.all([
    api.get("/users/", { params: { role: "expert" } }).then((r) => r.data),
    api.get("/projects/").then((r) => r.data),
  ]);
  if (!experts.length) return null;

  const load = {};
  experts.forEach((e) => { load[e.id] = 0; });
  projects.forEach((p) => {
    if (p.expert_id && load[p.expert_id] !== undefined) load[p.expert_id]++;
  });

  const best = experts.reduce((a, b) => (load[a.id] <= load[b.id] ? a : b));
  return updateProject(project.id, { expert_id: best.id, status: "на экспертизе" });
};

// ---------- Итоговый балл с коэффициентами ----------
export const calcFinalScore = (scores, weights) => {
  if (!scores) return 0;
  let sum = 0, total = 0;
  Object.keys(weights).forEach((k) => {
    const s = Number(scores[k] || 0);
    sum += s * weights[k];
    total += weights[k];
  });
  return total ? +(sum / total).toFixed(2) : 0;
};