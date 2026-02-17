import React from "react";
import { useNavigate } from "react-router-dom";
import "../styles/Home.css";

const Home: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="home-container">
      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-content">
          <h1 className="hero-title">Clinical Note Summarizer</h1>
          <p className="hero-subtitle">
            Intelligent NLP-Powered Clinical Documentation Analysis
          </p>
          <p className="hero-description">
            Automatically analyze clinical notes, detect risk factors, and
            generate structured summaries for healthcare professionals
          </p>

          <div className="hero-actions">
            <button
              className="btn btn-primary btn-large"
              onClick={() => navigate("/create-case")}
            >
              ➕ Create New Case
            </button>
            <button
              className="btn btn-secondary btn-large"
              onClick={() => navigate("/patient-cases")}
            >
              📋 View Cases
            </button>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features-section">
        <h2>Key Features</h2>
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">📝</div>
            <h3>Smart Summarization</h3>
            <p>
              Automatically extract chief complaints, key findings, and
              assessments from clinical notes
            </p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">⚠️</div>
            <h3>Risk Detection</h3>
            <p>
              Identify critical risk words and analyze patient-specific risk
              factors
            </p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">🏥</div>
            <h3>ICD Code Generation</h3>
            <p>
              Automatically generate relevant ICD codes based on clinical
              documentation
            </p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">📊</div>
            <h3>Confidence Scoring</h3>
            <p>
              Get confidence scores for each analysis to ensure quality and
              reliability
            </p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">🔄</div>
            <h3>Microservices Architecture</h3>
            <p>
              Built with modular, scalable architecture for reliable performance
            </p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">🐳</div>
            <h3>Docker Deployment</h3>
            <p>Single-command deployment with Docker Compose for easy setup</p>
          </div>
        </div>
      </section>

      {/* Quick Stats Section */}
      <section className="stats-section">
        <h2>Application Overview</h2>
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-number">3</div>
            <div className="stat-label">Microservices</div>
            <small>Frontend, Backend, NLP Service</small>
          </div>
          <div className="stat-card">
            <div className="stat-number">&lt;2s</div>
            <div className="stat-label">Response Time</div>
            <small>For summarization requests</small>
          </div>
          <div className="stat-card">
            <div className="stat-number">95%</div>
            <div className="stat-label">Max Confidence</div>
            <small>Accuracy scoring</small>
          </div>
          <div className="stat-card">
            <div className="stat-number">6</div>
            <div className="stat-label">Months</div>
            <small>Development timeline</small>
          </div>
        </div>
      </section>

      {/* Getting Started Section */}
      <section className="getting-started-section">
        <h2>Getting Started</h2>
        <div className="getting-started-grid">
          <div className="step-card">
            <div className="step-number">1</div>
            <h3>Create a Case</h3>
            <p>
              Enter patient information and clinical notes to create a new case
            </p>
            <button
              className="btn btn-outline"
              onClick={() => navigate("/create-case")}
            >
              Go to Create Case
            </button>
          </div>

          <div className="step-card">
            <div className="step-number">2</div>
            <h3>View Cases</h3>
            <p>
              Browse all patient cases with quick access to summaries and
              details
            </p>
            <button
              className="btn btn-outline"
              onClick={() => navigate("/patient-cases")}
            >
              Go to Patient Cases
            </button>
          </div>

          <div className="step-card">
            <div className="step-number">3</div>
            <h3>Summarize</h3>
            <p>
              Click summarize to generate AI-powered clinical summaries and risk
              analysis
            </p>
            <button
              className="btn btn-outline"
              onClick={() => navigate("/patient-cases")}
            >
              Start Summarizing
            </button>
          </div>
        </div>
      </section>

      {/* Footer Section */}
      <footer className="home-footer">
        <div className="footer-content">
          <p>
            &copy; 2026 Clinical Summarizer. Built with React, Spring Boot, and
            FastAPI.
          </p>
          <div className="footer-links">
            <a href="#features">Features</a>
            <a href="#tech-stack">Technology</a>
            <a href="#contact">Contact</a>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Home;
