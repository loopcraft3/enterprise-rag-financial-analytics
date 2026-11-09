import axios from "axios";

import { getSessionId, markServerAwake } from "./session";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://127.0.0.1:8000",
});

// Tell the server which chat this request belongs to (unless the call already set it).
api.interceptors.request.use((config) => {
  if (!config.headers["X-Session-Id"]) {
    config.headers["X-Session-Id"] = getSessionId();
  }

  return config;
});

// Any real answer from our server means it is awake.
// (5xx can also come from the hosting proxy while the server is still starting, so it does not count.)
api.interceptors.response.use(
  (response) => {
    markServerAwake();
    return response;
  },
  (error) => {
    if (error.response && error.response.status < 500) {
      markServerAwake();
    }

    return Promise.reject(error);
  }
);

export default api;
