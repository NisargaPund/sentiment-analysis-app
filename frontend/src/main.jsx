import React from "react";
import { createRoot } from "react-dom/client";
import App from "./pages/App.jsx";
import AdminApp from "./pages/AdminApp.jsx";
import "./styles.css";

const isAdmin = window.location.pathname.startsWith("/admin");
createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    {isAdmin ? <AdminApp /> : <App />}
  </React.StrictMode>
);

