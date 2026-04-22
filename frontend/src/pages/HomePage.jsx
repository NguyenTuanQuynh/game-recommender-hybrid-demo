import { useEffect, useState } from "react";
import GameRow from "../components/GameRow";
import Loading from "../components/Loading";
import { getGames, getHomeRecommendations } from "../api/client";
import { safeLogEvent } from "../utils/tracking";

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

        safeLogEvent({
          event_type: "view_home",
          event_value: 0.1,
          source: "home",
          metadata: { page: "home" },
        });

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

        <div className="hero-meta">
          <span className="strategy-pill">
            Strategy: {recommendData?.strategy || "unknown"}
          </span>
          <span className="tip-text">
            Tip: click a few games, search, then come back home to see the recommendations change.
          </span>
        </div>
      </div>

      <GameRow
        title={`Recommended For You (${recommendData?.strategy || "unknown"})`}
        games={recommendData?.items || []}
        source="home"
      />

      <GameRow
        title="Popular Games"
        games={popularData?.items || []}
        source="home"
      />
    </div>
  );
}