import api from "./client";
export const getExpertWorks = (expertId) =>
  api.get(`/projects?expertId=${expertId}`).then((r) => r.data);
export const scoreProject = (id, scores) =>
  api.patch(`/projects/${id}`, { scores, status: "оценена" }).then((r) => r.data);