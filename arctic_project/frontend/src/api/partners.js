import api from "./client";

export const getPartners = () => api.get("/partners").then((r) => r.data);