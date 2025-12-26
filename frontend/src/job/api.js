import axios from "axios";

const API_URL = "http://localhost:8000";

export const loadRepo = async (repoUrl) => {
  const res = await axios.post(`${API_URL}/load_repo`, { repo_url: repoUrl });
  return res.data;
};

export const askQuestion = async (repoId, question) => {
  const res = await axios.post(`${API_URL}/ask`, { repo_id: repoId, question });
  return res.data;
};
