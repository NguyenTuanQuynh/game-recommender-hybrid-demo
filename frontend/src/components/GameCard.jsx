import { Link } from "react-router-dom";

export default function GameCard({ game }) {
  if (!game) return null;

  return (
    <Link to={`/games/${game.game_id}`} className="game-card-link">
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