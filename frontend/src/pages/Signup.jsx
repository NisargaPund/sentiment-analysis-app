import React, { useState } from "react";
import { api } from "../lib/api.js";
import Input from "../components/Input.jsx";
import Button from "../components/Button.jsx";

export default function Signup({ onSuccess, onSwitch }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  return (
    <div className="mx-auto max-w-md rounded-2xl border border-slate-900 bg-slate-950/40 p-4 sm:p-6 shadow-xl shadow-black/20">
      <h1 className="text-lg font-semibold sm:text-xl">Signup</h1>
      <p className="mt-1 text-xs sm:text-sm text-slate-400">Create an account to analyze Twitter news sentiment.</p>

      <form
        className="mt-6 space-y-4"
        onSubmit={async (e) => {
          e.preventDefault();
          setError("");
          setBusy(true);
          try {
            const res = await api.signup(username, password);
            onSuccess(res.user);
          } catch (err) {
            setError(err.message || "Signup failed");
          } finally {
            setBusy(false);
          }
        }}
      >
        <Input label="Username" value={username} onChange={setUsername} placeholder="e.g. nirjaala" />
        <Input
          label="Password (min 6 chars)"
          value={password}
          onChange={setPassword}
          type="password"
          placeholder="••••••••"
        />
        {error ? <div className="text-sm text-red-400">{error}</div> : null}
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <Button type="submit" disabled={busy}>
            {busy ? "Creating…" : "Signup"}
          </Button>
          <button type="button" className="text-xs sm:text-sm text-slate-300 hover:text-white text-center" onClick={onSwitch}>
            I already have an account
          </button>
        </div>
      </form>
    </div>
  );
}

