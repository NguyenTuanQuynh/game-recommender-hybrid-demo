import { useEffect, useMemo, useState } from "react";
import { getGames } from "../api/client";
import GameGrid from "../components/GameGrid";
import Loading from "../components/Loading";

export default function LibraryPage() {
  const [data, setData] = useState(null);
  const [sortBy, setSortBy] = useState("popular");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function fetchLibrary() {
      try {
        setLoading(true);
        setError("");

        const result = await getGames(80, 0);
        setData(result);
      } catch (err) {
        setError(err.message || "Failed to load library.");
      } finally {
        setLoading(false);
      }
    }

    fetchLibrary();
  }, []);

  const sortedGames = useMemo(() => {
    const items = [...(data?.items || [])];

    if (sortBy === "rating") {
      return items.sort((a, b) => (b.avg_rating || 0) - (a.avg_rating || 0));
    }

    if (sortBy === "title") {
      return items.sort((a, b) => (a.title || "").localeCompare(b.title || ""));
    }

    return items.sort((a, b) => (b.popularity_score || 0) - (a.popularity_score || 0));
  }, [data, sortBy]);

  if (loading) return <Loading text="Loading library..." />;
  if (error) return <div className="error-box">{error}</div>;

  return (
    <div className="page">
      <div className="page-header library-header">
        <div>
          <h1>Library</h1>
          <p className="muted-text">
            Browse the game catalog in a compact grid layout.
          </p>
        </div>

        <div className="library-controls">
          <label htmlFor="sortBy" className="muted-text">Sort by</label>
          <select
            id="sortBy"
            className="select-control"
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
          >
            <option value="popular">Popularity</option>
            <option value="rating">Rating</option>
            <option value="title">Title</option>
          </select>
        </div>
      </div>

      <GameGrid
        games={sortedGames}
        source="library"
      />
    </div>
  );
}