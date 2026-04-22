import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import GameRow from "../components/GameRow";
import Loading from "../components/Loading";
import {
  getGames,
  getHomeRecommendations,
  getRecentlyWatched,
} from "../api/client";
import { safeLogEvent } from "../utils/tracking";

export default function HomePage() {
  const [recommendData, setRecommendData] = useState(null);
  const [recentData, setRecentData] = useState(null);
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

        const [recommendRes, recentRes, popularRes] = await Promise.all([
          getHomeRecommendations("demo_user", 10, 0),
          getRecentlyWatched("demo_user", 10, 0),
          getGames(10, 0),
        ]);

        setRecommendData(recommendRes);
        setRecentData(recentRes);
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
      <div className="hero-banner compact-hero">
        <div className="hero-content">
          <div>
            <h1>Hybrid Game Recommender</h1>
            <p className="hero-subtext">
              Personalized homepage, search, similar-item recommendation, and live behavior logging.
            </p>
          </div>

          <div className="hero-actions">
            <span className="strategy-pill">
              Strategy: {recommendData?.strategy || "unknown"}
            </span>

            <Link to="/library" className="ghost-button">
              Open Library
            </Link>
          </div>
        </div>
      </div>

      <GameRow
        title="Recommended For You"
        games={recommendData?.items || []}
        source="home"
      />

      {recentData?.items?.length > 0 ? (
        <GameRow
          title="Just Watched"
          games={recentData?.items || []}
          source="recent"
        />
      ) : null}

      <GameRow
        title="Popular Games"
        games={popularData?.items || []}
        source="home"
      />
    </div>
  );
}