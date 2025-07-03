import axios from "axios";

// TODO: make host and port configurable using env var
const axiosInstance = axios.create({
  baseURL: "http://127.0.0.1:5000/api/v1",
  headers: {
    Accept: "application/json",
    "Content-Type": "application/json",
  },
});

export default axiosInstance;
