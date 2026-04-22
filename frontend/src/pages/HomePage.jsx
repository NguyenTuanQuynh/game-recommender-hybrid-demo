import { useEffect, useState } from "react";
import GameRow from "../components/GameRow";
import Loading from "../components/Loading";
import { getGames, getHomeRecommendations } from "../api/client";

export default function HomePage() {
  const [recommendData, setRecommendData] = useState(null);
  const [popularData, setPopularData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function fetchHomeData() {
      try {
        setLoading(true);
        setError("");

        const [recommendRes, popularRes] = await Promise.all([
          getHomeRecommendations("demo_user", 12, 0),
          getGames(12, 0),
        ]);

        setRecommendData(recommendRes);
        setPopularData(popularRes);
      } catch (err) {
        setError(err.message || "Failed to load homepage.");
      } finally {
        setLoading(false);
      }
    }

    fetchHomeData();
  }, []);

  if (loading) return <Loading text="Loading homepage..." />;
  if (error) return <div className="error-box">{error}</div>;

  return (
    <div className="page">
      <div className="hero-banner">
        <h1>Hybrid Game Recommender</h1>
        <p>
          Demo homepage with personalized recommendations, popular games, search,
          and similar-item recommendation.
        </p>
      </div>

      <GameRow
        title={`Recommended For You (${recommendData?.strategy || "unknown"})`}
        games={recommendData?.items || []}
      />

      <GameRow
        title="Popular Games"
        games={popularData?.items || []}
      />
    </div>
  );
}