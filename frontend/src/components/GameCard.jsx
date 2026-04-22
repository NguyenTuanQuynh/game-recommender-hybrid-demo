import { Link } from "react-router-dom";
import { safeLogEvent } from "../utils/tracking";

function getClickEventType(source) {
  if (source === "search") return "click_search_result";
  if (source === "similar") return "click_similar_item";
  return "click_poster";
}

function getClickEventValue(source) {
  if (source === "search") return 2.0;
  if (source === "similar") return 1.5;
  return 1.0;
}

export default function GameCard({ game, source = "home", query = null }) {
  if (!game) return null;

  const handleClick = () => {
    safeLogEvent({
      event_type: getClickEventType(source),
      game_id: game.game_id,
      event_value: getClickEventValue(source),
      query: source === "search" ? query : null,
      source,
      metadata: {
        title: game.title,
      },
    });
  };

  return (
    <Link to={`/games/${game.game_id}`} className="game-card-link" onClick={handleClick}>
      <div
        className="game-card"
        style={{ backgroundColor: game.ui_color || "#2d3748" }}
      >
        <div className="game-card-label">
          {game.display_label || game.title || game.game_id}
        </div>

        <div className="game-card-meta">
          <div className="game-card-title">{game.title}</div>
          <div className="game-card-subtitle">
            {game.categories_text || "No category"}
          </div>
        </div>
      </div>
    </Link>
  );
}