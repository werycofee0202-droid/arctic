import api from "./client";
export const getParticipantsCount = () =>
  api.get("/stats/participants").then((r) => r.data.count);