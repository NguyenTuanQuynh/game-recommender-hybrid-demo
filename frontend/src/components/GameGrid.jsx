import GameCard from "./GameCard";

export default function GameGrid({ title, games = [], source = "library", query = null }) {
  return (
    <section className="game-grid-section">
      {title ? <h2 className="section-title">{title}</h2> : null}

      {games.length === 0 ? (
        <div className="empty-text">No games found.</div>
      ) : (
        <div className="game-grid">
          {games.map((game) => (
            <GameCard
              key={game.game_id}
              game={game}
              source={source}
              query={query}
            />
          ))}
        </div>
      )}
    </section>
  );
}