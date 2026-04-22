import { Link, NavLink, Route, Routes } from "react-router-dom";
import SearchBar from "./components/SearchBar";
import HomePage from "./pages/HomePage";
import DetailPage from "./pages/DetailPage";
import SearchPage from "./pages/SearchPage";
import LibraryPage from "./pages/LibraryPage";

function navClassName({ isActive }) {
  return isActive ? "nav-link nav-link-active" : "nav-link";
}

export default function App() {
  return (
    <div className="app-shell">
      <header className="topbar refined-topbar">
        <div className="topbar-left">
          <Link to="/" className="brand">
            Hybrid Game Recommender
          </Link>

          <nav className="nav-links">
            <NavLink to="/" end className={navClassName}>
              Home
            </NavLink>
            <NavLink to="/library" className={navClassName}>
              Library
            </NavLink>
          </nav>
        </div>

        <div className="topbar-right">
          <SearchBar />
        </div>
      </header>

      <main className="main-content">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/library" element={<LibraryPage />} />
          <Route path="/games/:gameId" element={<DetailPage />} />
          <Route path="/search" element={<SearchPage />} />
        </Routes>
      </main>
    </div>
  );
}