import React, { useEffect, useState } from "react";
import { api } from "../lib/api.js";

const TABS = ["Overview", "Users", "Searches", "Activity Log", "Export"];

function formatDate(dateString) {
  try {
    return new Date(dateString).toLocaleString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return dateString;
  }
}

export default function AdminDashboard({ onLogout }) {
  const [tab, setTab] = useState("Overview");
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [searches, setSearches] = useState([]);
  const [activities, setActivities] = useState([]);
  const [totalActivities, setTotalActivities] = useState(0);
  const [activityOffset, setActivityOffset] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [exportData, setExportData] = useState(null);

  const loadStats = async () => {
    try {
      const data = await api.admin.getStatistics();
      setStats(data);
    } catch (e) {
      setError(e.message);
    }
  };

  const loadUsers = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await api.admin.getUsers();
      setUsers(data.users || []);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const loadSearches = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await api.admin.getSearches();
      setSearches(data.searches || []);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const loadActivity = async (offset = 0) => {
    setLoading(true);
    setError("");
    try {
      const data = await api.admin.getActivity(100, offset);
      setActivities(data.activities || []);
      setTotalActivities(data.total || 0);
      setActivityOffset(offset);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const loadExport = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await api.admin.exportAll();
      setExportData(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadStats();
  }, []);

  useEffect(() => {
    if (tab === "Users") loadUsers();
    if (tab === "Searches") loadSearches();
    if (tab === "Activity Log") loadActivity(0);
    if (tab === "Export") loadExport();
  }, [tab]);

  const downloadExport = () => {
    if (!exportData) return;
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: "application/json" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `admin-export-${new Date().toISOString().slice(0, 10)}.json`;
    a.click();
    URL.revokeObjectURL(a.href);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <h1 className="text-xl font-semibold">Admin Panel</h1>
        <div className="flex items-center gap-3">
          <a href="/" className="text-sm text-slate-400 hover:text-white">App</a>
          <button onClick={onLogout} className="text-sm text-slate-400 hover:text-white">
            Logout
          </button>
        </div>
      </div>

      <div className="flex flex-wrap gap-2 border-b border-slate-800 pb-2">
        {TABS.map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`rounded-lg px-3 py-1.5 text-sm font-medium transition-colors ${
              tab === t ? "bg-slate-700 text-white" : "text-slate-400 hover:bg-slate-800 hover:text-white"
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      {error && (
        <div className="rounded-lg bg-red-950/50 border border-red-900/50 p-3 text-sm text-red-300">
          {error}
        </div>
      )}

      {tab === "Overview" && (
        <div className="rounded-2xl border border-slate-900 bg-slate-950/40 p-6">
          <h2 className="text-lg font-semibold mb-4">Statistics</h2>
          {stats ? (
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="rounded-xl bg-slate-900/60 p-4">
                <div className="text-2xl font-bold text-white">{stats.total_users}</div>
                <div className="text-sm text-slate-400">Total users</div>
              </div>
              <div className="rounded-xl bg-slate-900/60 p-4">
                <div className="text-2xl font-bold text-white">{stats.total_searches}</div>
                <div className="text-sm text-slate-400">Searches / analyses</div>
              </div>
              <div className="rounded-xl bg-slate-900/60 p-4">
                <div className="text-2xl font-bold text-white">{stats.total_activities}</div>
                <div className="text-sm text-slate-400">Activity log entries</div>
              </div>
            </div>
          ) : (
            <div className="text-slate-400">Loading…</div>
          )}
        </div>
      )}

      {tab === "Users" && (
        <div className="rounded-2xl border border-slate-900 bg-slate-950/40 overflow-hidden">
          <div className="p-4 border-b border-slate-800">
            <h2 className="text-lg font-semibold">Users</h2>
            <p className="text-sm text-slate-400">All registered user accounts.</p>
          </div>
          {loading ? (
            <div className="p-6 text-slate-400">Loading…</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead>
                  <tr className="border-b border-slate-800 bg-slate-900/40">
                    <th className="p-3 font-medium">ID</th>
                    <th className="p-3 font-medium">Username</th>
                    <th className="p-3 font-medium">Admin</th>
                    <th className="p-3 font-medium">Created</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((u) => (
                    <tr key={u.id} className="border-b border-slate-800/60">
                      <td className="p-3">{u.id}</td>
                      <td className="p-3">{u.username}</td>
                      <td className="p-3">{u.is_admin ? "Yes" : "No"}</td>
                      <td className="p-3 text-slate-400">{formatDate(u.created_at)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {tab === "Searches" && (
        <div className="rounded-2xl border border-slate-900 bg-slate-950/40 overflow-hidden">
          <div className="p-4 border-b border-slate-800">
            <h2 className="text-lg font-semibold">Searches / Analyses</h2>
            <p className="text-sm text-slate-400">Sentiment analysis history (last 500).</p>
          </div>
          {loading ? (
            <div className="p-6 text-slate-400">Loading…</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead>
                  <tr className="border-b border-slate-800 bg-slate-900/40">
                    <th className="p-3 font-medium">ID</th>
                    <th className="p-3 font-medium">User ID</th>
                    <th className="p-3 font-medium">Keyword</th>
                    <th className="p-3 font-medium">Pos / Neu / Neg</th>
                    <th className="p-3 font-medium">Created</th>
                  </tr>
                </thead>
                <tbody>
                  {searches.map((s) => (
                    <tr key={s.id} className="border-b border-slate-800/60">
                      <td className="p-3">{s.id}</td>
                      <td className="p-3">{s.user_id}</td>
                      <td className="p-3">{s.keyword}</td>
                      <td className="p-3 text-slate-400">
                        {Number(s.positive).toFixed(2)} / {Number(s.neutral).toFixed(2)} / {Number(s.negative).toFixed(2)}
                      </td>
                      <td className="p-3 text-slate-400">{formatDate(s.created_at)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {tab === "Activity Log" && (
        <div className="rounded-2xl border border-slate-900 bg-slate-950/40 overflow-hidden">
          <div className="p-4 border-b border-slate-800 flex flex-wrap items-center justify-between gap-2">
            <div>
              <h2 className="text-lg font-semibold">Activity Log</h2>
              <p className="text-sm text-slate-400">Every action is stored (signup, login, fetch news, analyze, admin).</p>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs text-slate-500">{activityOffset + 1}–{activityOffset + activities.length} of {totalActivities}</span>
              <button
                onClick={() => loadActivity(Math.max(0, activityOffset - 100))}
                disabled={activityOffset === 0}
                className="rounded bg-slate-700 px-2 py-1 text-xs disabled:opacity-50"
              >
                Prev
              </button>
              <button
                onClick={() => loadActivity(activityOffset + 100)}
                disabled={activityOffset + activities.length >= totalActivities}
                className="rounded bg-slate-700 px-2 py-1 text-xs disabled:opacity-50"
              >
                Next
              </button>
            </div>
          </div>
          {loading ? (
            <div className="p-6 text-slate-400">Loading…</div>
          ) : (
            <div className="overflow-x-auto max-h-[60vh] overflow-y-auto">
              <table className="w-full text-left text-sm">
                <thead className="sticky top-0 bg-slate-950 z-10">
                  <tr className="border-b border-slate-800 bg-slate-900/40">
                    <th className="p-3 font-medium">Time</th>
                    <th className="p-3 font-medium">Action</th>
                    <th className="p-3 font-medium">Actor</th>
                    <th className="p-3 font-medium">User ID</th>
                    <th className="p-3 font-medium">Payload</th>
                    <th className="p-3 font-medium">IP</th>
                  </tr>
                </thead>
                <tbody>
                  {activities.map((a) => (
                    <tr key={a.id} className="border-b border-slate-800/60">
                      <td className="p-3 text-slate-400 whitespace-nowrap">{formatDate(a.created_at)}</td>
                      <td className="p-3 font-medium">{a.action}</td>
                      <td className="p-3">{a.actor_type}</td>
                      <td className="p-3">{a.user_id ?? "—"}</td>
                      <td className="p-3 text-slate-400 max-w-xs truncate" title={a.payload}>
                        {a.payload ? (typeof a.payload === "string" ? a.payload : JSON.stringify(a.payload)).slice(0, 80) + "…" : "—"}
                      </td>
                      <td className="p-3 text-slate-500 text-xs">{a.ip_address || "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {tab === "Export" && (
        <div className="rounded-2xl border border-slate-900 bg-slate-950/40 p-6">
          <h2 className="text-lg font-semibold mb-2">Export all data</h2>
          <p className="text-sm text-slate-400 mb-4">
            Download a JSON file containing users, searches, and the full activity log.
          </p>
          {loading ? (
            <div className="text-slate-400">Loading…</div>
          ) : exportData ? (
            <div className="space-y-2">
              <p className="text-sm text-slate-300">
                Users: {exportData.users?.length ?? 0} · Searches: {exportData.searches?.length ?? 0} · Activities: {exportData.activity_log?.length ?? 0}
              </p>
              <button
                onClick={downloadExport}
                className="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-700"
              >
                Download JSON
              </button>
            </div>
          ) : (
            <p className="text-slate-500">No data loaded.</p>
          )}
        </div>
      )}
    </div>
  );
}
