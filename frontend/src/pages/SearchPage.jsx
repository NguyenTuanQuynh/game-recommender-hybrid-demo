import { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import GameRow from "../components/GameRow";
import Loading from "../components/Loading";
import { searchGames } from "../api/client";
import { safeLogEvent } from "../utils/tracking";

export default function SearchPage() {
  const location = useLocation();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const params = new URLSearchParams(location.search);
  const query = params.get("q") || "";

  useEffect(() => {
    async function fetchSearch() {
      if (!query.trim()) {
        setData({ items: [], total: 0, query: "" });
        return;
      }

      try {
        setLoading(true);
        setError("");

        safeLogEvent({
          event_type: "search",
          event_value: 0.5,
          query,
          source: "search",
          metadata: { page: "search" },
        });

        const result = await searchGames(query, 20, 0);
        setData(result);
      } catch (err) {
        setError(err.message || "Search failed.");
      } finally {
        setLoading(false);
      }
    }

    fetchSearch();
  }, [query]);

  if (loading) return <Loading text="Searching..." />;
  if (error) return <div className="error-box">{error}</div>;

  return (
    <div className="page">
      <div className="page-header">
        <h1>Search Results</h1>
        <p>
          Query: <strong>{data?.query || query || "(empty)"}</strong>
        </p>
        <p>Total results: {data?.total || 0}</p>
      </div>

      <GameRow
        title="Matched Games"
        games={data?.items || []}
        source="search"
        query={query}
      />
    </div>
  );
}