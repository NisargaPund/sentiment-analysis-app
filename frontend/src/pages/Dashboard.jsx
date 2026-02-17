import React, { useEffect, useMemo, useState } from "react";
import { Pie } from "react-chartjs-2";
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from "chart.js";
import { api } from "../lib/api.js";
import Input from "../components/Input.jsx";
import Button from "../components/Button.jsx";

ChartJS.register(ArcElement, Tooltip, Legend);

export default function Dashboard() {
  // Load trending topics on mount
  useEffect(() => {
    (async () => {
      try {
        const res = await api.getTrending();
        setTrendingTopics(res.topics || []);
      } catch (err) {
        console.error("Failed to load trending topics:", err);
      } finally {
        setLoadingTopics(false);
      }
    })();
  }, []);
  const [keyword, setKeyword] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [trendingTopics, setTrendingTopics] = useState([]);
  const [loadingTopics, setLoadingTopics] = useState(true);
  const [selectedTopic, setSelectedTopic] = useState(null);
  const [newsItems, setNewsItems] = useState([]);
  const [loadingNews, setLoadingNews] = useState(false);
  const [selectedNews, setSelectedNews] = useState(null);

  const chartData = useMemo(() => {
    const s = result?.sentiment || { positive: 0, neutral: 0, negative: 0 };
    return {
      labels: ["Positive", "Neutral", "Negative"],
      datasets: [
        {
          label: "Sentiment (%)",
          data: [s.positive, s.neutral, s.negative],
          backgroundColor: ["#22c55e", "#94a3b8", "#ef4444"],
          borderColor: ["#16a34a", "#64748b", "#dc2626"],
          borderWidth: 1
        }
      ]
    };
  }, [result]);

  const handleTopicSelect = (topic) => {
    setSelectedTopic(topic);
    setKeyword(topic.title);
    setResult(null); // Clear previous results
    setNewsItems([]); // Clear previous news
    setSelectedNews(null); // Clear selected news
  };

  const handleFetchNews = async () => {
    if (!keyword.trim()) {
      setError("Please select a topic first");
      return;
    }
    setError("");
    setLoadingNews(true);
    setNewsItems([]);
    setSelectedNews(null);
    setResult(null);
    try {
      const res = await api.fetchNews(keyword);
      if (res.news_items && res.news_items.length > 0) {
        setNewsItems(res.news_items);
      } else {
        setError(res.message || "No news found for this topic");
      }
    } catch (err) {
      setError(err.message || "Failed to fetch news");
    } finally {
      setLoadingNews(false);
    }
  };

  const handleNewsSelect = (newsItem) => {
    setSelectedNews(newsItem);
    setResult(null); // Clear previous analysis
  };

  const handleAnalyze = async () => {
    if (!selectedNews) {
      setError("Please select a news item to analyze");
      return;
    }
    setError("");
    setBusy(true);
    try {
      const res = await api.analyze(selectedNews.text, keyword);
      setResult(res);
    } catch (err) {
      setError(err.message || "Analysis failed");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="space-y-4 sm:space-y-8">
      {/* Trending Topics Section */}
      <div className="rounded-2xl border border-slate-900 bg-slate-950/40 p-4 sm:p-6">
        <h2 className="text-lg font-semibold sm:text-xl">Trending Topics & News</h2>
        <p className="mt-1 text-xs sm:text-sm text-slate-400">
          Select a trending topic to analyze sentiment, or enter a custom keyword below.
        </p>

        {loadingTopics ? (
          <div className="mt-6 text-sm text-slate-400">Loading topics...</div>
        ) : (
          <div className="mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {trendingTopics.map((topic) => (
              <button
                key={topic.id}
                onClick={() => handleTopicSelect(topic)}
                className={`rounded-lg border p-4 text-left transition-all hover:border-purple-500 ${
                  selectedTopic?.id === topic.id
                    ? "border-purple-500 bg-purple-500/10"
                    : "border-slate-900 bg-slate-900/40"
                }`}
              >
                <div className="font-semibold text-slate-100">{topic.title}</div>
                <div className="mt-1 text-xs text-slate-400">{topic.category}</div>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Fetch News Section */}
      {selectedTopic && (
        <div className="rounded-2xl border border-slate-900 bg-slate-950/40 p-4 sm:p-6">
          <h2 className="text-lg font-semibold sm:text-xl">Fetch News</h2>
          <p className="mt-1 text-xs sm:text-sm text-slate-400">
            Selected topic: <span className="font-semibold text-purple-400">{keyword}</span>
          </p>
          <div className="mt-4">
            <Button onClick={handleFetchNews} disabled={loadingNews || !keyword.trim()}>
              {loadingNews ? "Fetching News…" : "Fetch News"}
            </Button>
          </div>
        </div>
      )}

      {/* News Items List */}
      {newsItems.length > 0 && (
        <div className="rounded-2xl border border-slate-900 bg-slate-950/40 p-4 sm:p-6">
          <h2 className="text-lg font-semibold sm:text-xl">News Items ({newsItems.length} found)</h2>
          <p className="mt-1 text-xs sm:text-sm text-slate-400">
            Select a news item to analyze its sentiment
          </p>
          <div className="mt-4 space-y-3 max-h-96 overflow-y-auto">
            {newsItems.map((item) => (
              <button
                key={item.id}
                onClick={() => handleNewsSelect(item)}
                className={`w-full rounded-lg border p-3 sm:p-4 text-left transition-all hover:border-purple-500 ${
                  selectedNews?.id === item.id
                    ? "border-purple-500 bg-purple-500/10"
                    : "border-slate-900 bg-slate-900/40"
                }`}
              >
                <div className="text-xs sm:text-sm text-slate-300">{item.text}</div>
                {selectedNews?.id === item.id && (
                  <div className="mt-2 text-xs text-purple-400">✓ Selected for analysis</div>
                )}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Analysis Section */}
      {selectedNews && (
        <div className="rounded-2xl border border-slate-900 bg-slate-950/40 p-4 sm:p-6">
          <h2 className="text-lg font-semibold sm:text-xl">Sentiment Analysis</h2>
          <p className="mt-1 text-xs sm:text-sm text-slate-400">
            Selected news: <span className="font-semibold text-purple-400 break-words">{selectedNews.text.length > 50 ? selectedNews.text.substring(0, 50) + "..." : selectedNews.text}</span>
          </p>
          <div className="mt-4">
            <Button onClick={handleAnalyze} disabled={busy}>
              {busy ? "Analyzing…" : "Analyze Sentiment"}
            </Button>
          </div>
          {error ? <div className="mt-4 text-xs sm:text-sm text-red-400">{error}</div> : null}
        </div>
      )}

      {/* Results Section */}
      {result && (
        <>
          <div className="grid gap-4 sm:gap-6 grid-cols-1 sm:grid-cols-3">
            <Stat title="News Item Analyzed" value="1" />
            <Stat title="Positive (%)" value={`${result.sentiment.positive}%`} accent="text-green-400" />
            <Stat title="Negative (%)" value={`${result.sentiment.negative}%`} accent="text-red-400" />
          </div>
        </>
      )}

      {result && (
        <>
          <div className="grid gap-4 sm:gap-6 grid-cols-1 md:grid-cols-2">
            <div className="rounded-2xl border border-slate-900 bg-slate-950/40 p-4 sm:p-6">
              <div className="flex flex-col sm:flex-row sm:items-baseline sm:justify-between gap-2">
                <h3 className="text-base font-semibold sm:text-lg">Sentiment Chart</h3>
                <div className="text-xs text-slate-400">{result.topic ? `Topic: ${result.topic}` : "Analysis Result"}</div>
              </div>
              <div className="mt-4 sm:mt-6">
                <Pie data={chartData} />
              </div>
            </div>

            <div className="rounded-2xl border border-slate-900 bg-slate-950/40 p-4 sm:p-6">
              <h3 className="text-base font-semibold sm:text-lg">Neutral (%)</h3>
              <div className="mt-2 text-3xl sm:text-4xl font-bold text-slate-200">
                {result.sentiment.neutral}%
              </div>
              <div className="mt-4">
                <div className="text-xs sm:text-sm text-slate-400">Classification:</div>
                <div className={`mt-1 text-base sm:text-lg font-semibold ${
                  result.classification === "positive" ? "text-green-400" :
                  result.classification === "negative" ? "text-red-400" :
                  "text-slate-300"
                }`}>
                  {result.classification?.charAt(0).toUpperCase() + result.classification?.slice(1)} 
                  {result.confidence && ` (${result.confidence}% confidence)`}
                </div>
              </div>
            </div>
          </div>

          {/* Explanation Section */}
          {result.explanation && (
            <div className="rounded-2xl border border-slate-900 bg-slate-950/40 p-4 sm:p-6">
              <h3 className="text-base font-semibold sm:text-lg mb-3 sm:mb-4">Analysis Explanation</h3>
              <div className="rounded-lg border border-slate-800 bg-slate-900/40 p-3 sm:p-4">
                <div className="text-xs sm:text-sm text-slate-300 leading-relaxed whitespace-pre-line">
                  {result.explanation}
                </div>
              </div>
              
              {/* Key Words */}
              {(result.key_words?.positive?.length > 0 || result.key_words?.negative?.length > 0) && (
                <div className="mt-4 grid gap-4 grid-cols-1 sm:grid-cols-2">
                  {result.key_words.positive?.length > 0 && (
                    <div>
                      <div className="text-xs text-slate-400 mb-2">Positive Words Detected:</div>
                      <div className="flex flex-wrap gap-2">
                        {result.key_words.positive.map((word, idx) => (
                          <span key={idx} className="px-2 py-1 rounded bg-green-500/20 text-green-400 text-xs">
                            {word}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                  {result.key_words.negative?.length > 0 && (
                    <div>
                      <div className="text-xs text-slate-400 mb-2">Negative Words Detected:</div>
                      <div className="flex flex-wrap gap-2">
                        {result.key_words.negative.map((word, idx) => (
                          <span key={idx} className="px-2 py-1 rounded bg-red-500/20 text-red-400 text-xs">
                            {word}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Full News Text */}
              {result.full_text && (
                <div className="mt-4 rounded-lg border border-slate-800 bg-slate-900/40 p-3">
                  <div className="text-xs text-slate-400 mb-2">Analyzed News Item:</div>
                  <div className="text-xs sm:text-sm text-slate-300 break-words">{result.full_text}</div>
                </div>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
}

function Stat({ title, value, accent = "text-slate-100" }) {
  return (
    <div className="rounded-2xl border border-slate-900 bg-slate-950/40 p-4 sm:p-6">
      <div className="text-xs sm:text-sm text-slate-400">{title}</div>
      <div className={`mt-2 text-2xl sm:text-3xl font-bold ${accent}`}>{value}</div>
    </div>
  );
}

