import React, { useEffect, useState } from "react";
import { api } from "../lib/api.js";
import AdminLogin from "./AdminLogin.jsx";
import AdminDashboard from "./AdminDashboard.jsx";

export default function AdminApp() {
  const [admin, setAdmin] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const res = await api.admin.me();
        if (res.admin) {
          setAdmin(res.admin);
        }
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const handleLogout = async () => {
    try {
      await api.admin.logout();
    } catch (_) {}
    setAdmin(null);
  };

  if (loading) {
    return (
      <div className="min-h-screen grid place-items-center bg-slate-950">
        <div className="text-slate-300">Loading…</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-200">
      <header className="border-b border-slate-800">
        <div className="mx-auto max-w-5xl px-3 py-3 md:px-4 md:py-4">
          <div className="text-base font-semibold md:text-lg">Admin Panel · Sentiment App</div>
        </div>
      </header>
      <main className="mx-auto max-w-5xl px-3 py-6 sm:px-4 sm:py-10">
        {!admin ? (
          <AdminLogin onSuccess={() => setAdmin({ username: "admin" })} />
        ) : (
          <AdminDashboard onLogout={handleLogout} />
        )}
      </main>
    </div>
  );
}
