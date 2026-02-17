import React, { useEffect, useState } from "react";
import { api } from "../lib/api.js";
import Login from "./Login.jsx";
import Signup from "./Signup.jsx";
import Dashboard from "./Dashboard.jsx";
import History from "./History.jsx";

export default function App() {
  const [user, setUser] = useState(null);
  const [view, setView] = useState("login"); // login | signup | dashboard | history
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const res = await api.me();
        if (res.user) {
          setUser(res.user);
          setView("dashboard");
        }
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen grid place-items-center">
        <div className="text-slate-300">Loading…</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      <header className="border-b border-slate-900">
        <div className="mx-auto max-w-5xl px-3 py-3 md:px-4 md:py-4">
          <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div>
              <div className="text-base font-semibold md:text-lg">Twitter News Sentiment</div>
              <div className="text-xs text-slate-400 hidden sm:block">RoBERTa (cardiffnlp) • Twitter API v2</div>
              <a href="/admin" className="text-xs text-slate-500 hover:text-slate-300 mt-1 inline-block">Admin panel</a>
            </div>
            {user ? (
              <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:gap-4">
                <div className="flex gap-2 sm:gap-3">
                  <button
                    className={`text-xs sm:text-sm transition-colors ${
                      view === "dashboard"
                        ? "text-white font-semibold"
                        : "text-slate-400 hover:text-white"
                    }`}
                    onClick={() => setView("dashboard")}
                  >
                    Dashboard
                  </button>
                  <button
                    className={`text-xs sm:text-sm transition-colors ${
                      view === "history"
                        ? "text-white font-semibold"
                        : "text-slate-400 hover:text-white"
                    }`}
                    onClick={() => setView("history")}
                  >
                    History
                  </button>
                </div>
                <div className="hidden h-4 w-px bg-slate-700 sm:block" />
                <div className="text-xs sm:text-sm text-slate-300">
                  Signed in as <span className="font-semibold">{user.username}</span>
                </div>
                <button
                  className="text-xs sm:text-sm text-slate-300 hover:text-white"
                  onClick={async () => {
                    await api.logout();
                    setUser(null);
                    setView("login");
                  }}
                >
                  Logout
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-3 text-xs sm:text-sm">
                <button
                  className={`hover:text-white ${view === "login" ? "text-white" : "text-slate-400"}`}
                  onClick={() => setView("login")}
                >
                  Login
                </button>
                <button
                  className={`hover:text-white ${view === "signup" ? "text-white" : "text-slate-400"}`}
                  onClick={() => setView("signup")}
                >
                  Signup
                </button>
              </div>
            )}
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-5xl px-3 py-6 sm:px-4 sm:py-10">
        {!user && view === "login" && (
          <Login
            onSuccess={(u) => {
              setUser(u);
              setView("dashboard");
            }}
            onSwitch={() => setView("signup")}
          />
        )}
        {!user && view === "signup" && (
          <Signup
            onSuccess={(u) => {
              setUser(u);
              setView("dashboard");
            }}
            onSwitch={() => setView("login")}
          />
        )}
        {user && view === "dashboard" && <Dashboard />}
        {user && view === "history" && <History />}
      </main>
    </div>
  );
}

