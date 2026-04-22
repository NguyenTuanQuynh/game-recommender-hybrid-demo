import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import GameRow from "../components/GameRow";
import Loading from "../components/Loading";
import { getGameDetail, getSimilarGames } from "../api/client";
import { safeLogEvent } from "../utils/tracking";

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

        safeLogEvent({
          event_type: "view_detail",
          game_id: gameId,
          event_value: 2.0,
          source: "detail",
          metadata: { page: "detail" },
        });
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
      <div className="detail-layout refined-detail">
        <div
          className="detail-poster"
          style={{ backgroundColor: game.ui_color || "#2d3748" }}
        >
          <div className="detail-poster-label">
            {game.display_label || game.title || game.game_id}
          </div>
        </div>

        <div className="detail-info refined-detail-info">
          <div className="detail-id">{game.game_id}</div>
          <h1>{game.title}</h1>

          <div className="detail-meta">
            {game.categories_text ? (
              <span className="meta-pill">{game.categories_text}</span>
            ) : null}
            {game.brand ? <span className="meta-pill">{game.brand}</span> : null}
            {game.avg_rating !== null && game.avg_rating !== undefined ? (
              <span className="meta-pill">★ {Number(game.avg_rating).toFixed(1)}</span>
            ) : null}
            {game.price !== null && game.price !== undefined ? (
              <span className="meta-pill">${Number(game.price).toFixed(2)}</span>
            ) : null}
          </div>

          <p className="detail-description">
            {game.description || "No description available."}
          </p>

          <p className="muted-text">
            Rating count: {game.rating_count ?? "N/A"}
          </p>
        </div>
      </div>

      <GameRow
        title="More Like This"
        games={similar?.items || []}
        source="similar"
      />
    </div>
  );
}