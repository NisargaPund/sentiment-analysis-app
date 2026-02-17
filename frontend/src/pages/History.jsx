import React, { useEffect, useState } from "react";
import { api } from "../lib/api.js";

export default function History() {
  const [history, setHistory] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await api.getHistory();
      setHistory(data);
    } catch (err) {
      setError(err.message || "Failed to load history");
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleString("en-US", {
        year: "numeric",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit"
      });
    } catch {
      return dateString;
    }
  };

  const getSentimentColor = (sentiment) => {
    if (sentiment === "positive") return "text-green-400";
    if (sentiment === "negative") return "text-red-400";
    return "text-blue-400";
  };

  const getDominantSentiment = (positive, neutral, negative) => {
    if (positive >= neutral && positive >= negative) return "positive";
    if (negative >= neutral && negative >= positive) return "negative";
    return "neutral";
  };

  if (loading) {
    return (
      <div className="space-y-8">
        <div className="rounded-2xl border border-slate-900 bg-slate-950/40 p-6">
          <div className="text-center text-slate-400">Loading history...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-8">
        <div className="rounded-2xl border border-slate-900 bg-slate-950/40 p-6">
          <div className="text-center text-red-400">{error}</div>
          <div className="mt-4 text-center">
            <button
              onClick={loadHistory}
              className="rounded-lg bg-purple-600 px-4 py-2 text-sm font-semibold text-white hover:bg-purple-700"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  const stats = history?.statistics || {};
  const searches = history?.searches || [];

  return (
    <div className="space-y-4 sm:space-y-8">
      {/* Statistics Summary */}
      <div className="grid gap-4 sm:gap-6 grid-cols-2 md:grid-cols-4">
        <div className="rounded-2xl border border-slate-900 bg-slate-950/40 p-4 sm:p-6">
          <div className="text-xs sm:text-sm text-slate-400">Total Searches</div>
          <div className="mt-2 text-2xl sm:text-3xl font-bold text-slate-100">
            {stats.total_searches || 0}
          </div>
        </div>
        <div className="rounded-2xl border border-slate-900 bg-slate-950/40 p-4 sm:p-6">
          <div className="text-xs sm:text-sm text-slate-400">Tweets Analyzed</div>
          <div className="mt-2 text-2xl sm:text-3xl font-bold text-slate-100">
            {stats.total_tweets_analyzed || 0}
          </div>
        </div>
        <div className="rounded-2xl border border-slate-900 bg-slate-950/40 p-4 sm:p-6">
          <div className="text-xs sm:text-sm text-slate-400">Avg Positive</div>
          <div className="mt-2 text-2xl sm:text-3xl font-bold text-green-400">
            {stats.average_sentiment?.positive?.toFixed(1) || "0.0"}%
          </div>
        </div>
        <div className="rounded-2xl border border-slate-900 bg-slate-950/40 p-4 sm:p-6">
          <div className="text-xs sm:text-sm text-slate-400">Avg Negative</div>
          <div className="mt-2 text-2xl sm:text-3xl font-bold text-red-400">
            {stats.average_sentiment?.negative?.toFixed(1) || "0.0"}%
          </div>
        </div>
      </div>

      {/* Search History List */}
      <div className="rounded-2xl border border-slate-900 bg-slate-950/40 p-4 sm:p-6">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="text-lg font-semibold sm:text-xl">Search History</h2>
            <p className="mt-1 text-xs sm:text-sm text-slate-400">
              All your analyzed tweets and news items
            </p>
          </div>
          <button
            onClick={loadHistory}
            className="rounded-lg border border-slate-700 bg-slate-900/40 px-3 py-2 text-xs sm:text-sm font-semibold text-slate-300 hover:bg-slate-800 sm:px-4"
          >
            Refresh
          </button>
        </div>

        {searches.length === 0 ? (
          <div className="mt-8 text-center text-slate-400">
            <div className="text-lg">No search history yet</div>
            <div className="mt-2 text-sm">
              Start analyzing news items to see your history here!
            </div>
          </div>
        ) : (
          <div className="mt-6 space-y-4">
            {searches.map((search) => {
              const dominant = getDominantSentiment(
                search.positive,
                search.neutral,
                search.negative
              );
              return (
                <div
                  key={search.id}
                  className="rounded-lg border border-slate-800 bg-slate-900/20 p-3 sm:p-4 hover:border-slate-700"
                >
                  <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                    <div className="flex-1">
                      <div className="flex flex-wrap items-center gap-2 sm:gap-3">
                        <h3 className="text-sm sm:text-base font-semibold text-slate-100 break-words">
                          {search.keyword}
                        </h3>
                        <span
                          className={`rounded-full px-2 py-1 text-xs font-semibold ${getSentimentColor(
                            dominant
                          )} bg-slate-800`}
                        >
                          {dominant.toUpperCase()}
                        </span>
                      </div>
                      <div className="mt-2 flex flex-wrap gap-3 sm:gap-6 text-xs sm:text-sm">
                        <div>
                          <span className="text-slate-400">Tweets: </span>
                          <span className="font-semibold text-slate-200">
                            {search.tweet_count}
                          </span>
                        </div>
                        <div>
                          <span className="text-green-400">Positive: </span>
                          <span className="font-semibold text-green-300">
                            {search.positive.toFixed(1)}%
                          </span>
                        </div>
                        <div>
                          <span className="text-blue-400">Neutral: </span>
                          <span className="font-semibold text-blue-300">
                            {search.neutral.toFixed(1)}%
                          </span>
                        </div>
                        <div>
                          <span className="text-red-400">Negative: </span>
                          <span className="font-semibold text-red-300">
                            {search.negative.toFixed(1)}%
                          </span>
                        </div>
                      </div>
                    </div>
                    <div className="text-xs text-slate-500 sm:text-right">
                      {formatDate(search.created_at)}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
