import GameCard from "./GameCard";

export default function GameRow({ title, games = [] }) {
  return (
    <section className="game-row-section">
      <h2 className="section-title">{title}</h2>

      {games.length === 0 ? (
        <div className="empty-text">No games found.</div>
      ) : (
        <div className="game-row">
          {games.map((game) => (
            <GameCard key={game.game_id} game={game} />
          ))}
        </div>
      )}
    </section>
  );
}