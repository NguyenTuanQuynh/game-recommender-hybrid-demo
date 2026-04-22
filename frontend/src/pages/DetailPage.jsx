import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import GameRow from "../components/GameRow";
import Loading from "../components/Loading";
import { getGameDetail, getSimilarGames } from "../api/client";

export default function DetailPage() {
  const { gameId } = useParams();

  const [game, setGame] = useState(null);
  const [similar, setSimilar] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function fetchDetail() {
      try {
        setLoading(true);
        setError("");

        const [gameRes, similarRes] = await Promise.all([
          getGameDetail(gameId),
          getSimilarGames(gameId, 10, 0),
        ]);

        setGame(gameRes);
        setSimilar(similarRes);
      } catch (err) {
        setError(err.message || "Failed to load detail page.");
      } finally {
        setLoading(false);
      }
    }

    fetchDetail();
  }, [gameId]);

  if (loading) return <Loading text="Loading game detail..." />;
  if (error) return <div className="error-box">{error}</div>;
  if (!game) return <div className="error-box">Game not found.</div>;

  return (
    <div className="page">
      <div className="detail-layout">
        <div
          className="detail-poster"
          style={{ backgroundColor: game.ui_color || "#2d3748" }}
        >
          <div className="detail-poster-label">
            {game.display_label || game.title || game.game_id}
          </div>
        </div>

        <div className="detail-info">
          <h1>{game.title}</h1>
          <p><strong>Game ID:</strong> {game.game_id}</p>
          <p><strong>Categories:</strong> {game.categories_text || "N/A"}</p>
          <p><strong>Brand:</strong> {game.brand || "N/A"}</p>
          <p><strong>Price:</strong> {game.price ?? "N/A"}</p>
          <p><strong>Average Rating:</strong> {game.avg_rating ?? "N/A"}</p>
          <p><strong>Rating Count:</strong> {game.rating_count ?? "N/A"}</p>
          <p><strong>Description:</strong> {game.description || "No description"}</p>
        </div>
      </div>

      <GameRow
        title="Similar Games"
        games={similar?.items || []}
      />
    </div>
  );
}