import React from "react";
import { Link, useLocation } from "react-router-dom";
import "../styles/Navbar.css";

const Navbar: React.FC = () => {
  const location = useLocation();

  const isActive = (path: string) => location.pathname === path;

  return (
    <nav className="navbar">
      <div className="navbar-container">
        {/* Logo Section */}
        <div className="navbar-logo">
          <Link to="/" className="logo-link">
            <img
              src="/logo.png"
              alt="Clinical Summarizer"
              className="logo-image"
              onError={(e) => {
                // Fallback if logo not found
                const target = e.target as HTMLImageElement;
                target.style.display = "none";
              }}
            />
            <span className="logo-text">Clinical Summarizer</span>
          </Link>
        </div>

        {/* Navigation Links */}
        <ul className="navbar-items">
          <li>
            <Link
              to="/"
              className={`nav-link ${isActive("/") ? "active" : ""}`}
            >
              <span className="nav-icon">🏠</span>
              Home
            </Link>
          </li>
          <li>
            <Link
              to="/create-case"
              className={`nav-link ${isActive("/create-case") ? "active" : ""}`}
            >
              <span className="nav-icon">➕</span>
              Create Case
            </Link>
          </li>
          <li>
            <Link
              to="/patient-cases"
              className={`nav-link ${isActive("/patient-cases") ? "active" : ""}`}
            >
              <span className="nav-icon">📋</span>
              Patient Cases
            </Link>
          </li>
        </ul>

        {/* User Profile / Settings (optional) */}
        <div className="navbar-right">
          <button className="settings-btn" title="Settings">
            ⚙️
          </button>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
