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

function getPrimaryCategory(categoriesText) {
  if (!categoriesText) return "";
  return categoriesText
    .split("|")
    .map((x) => x.trim())
    .filter(Boolean)[0] || "";
}

export default function GameCard({ game, source = "home", query = null }) {
  if (!game) return null;

  const primaryCategory = getPrimaryCategory(game.categories_text);
  const ratingText =
    game.avg_rating !== null && game.avg_rating !== undefined
      ? Number(game.avg_rating).toFixed(1)
      : null;

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
        <div className="game-card-top">
          {primaryCategory ? (
            <span className="game-card-chip">{primaryCategory}</span>
          ) : (
            <span className="game-card-chip">Game</span>
          )}
        </div>

        <div className="game-card-bottom">
          <div className="game-card-title">
            {game.display_label || game.title || game.game_id}
          </div>

          <div className="game-card-footer">
            {ratingText ? <span className="game-card-rating">★ {ratingText}</span> : null}
          </div>
        </div>
      </div>
    </Link>
  );
}