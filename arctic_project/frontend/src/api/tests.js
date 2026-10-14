import api from "./client";

export const getTest = (id = 1) =>
  api.get(`/tests/${id}`).then((r) => r.data);

export const saveTestResult = (payload) =>
  api.post("/test-results", payload).then((r) => r.data);

export const saveCertificate = (payload) =>
  api.post("/certificates", payload).then((r) => r.data);
