import React, { useState, useEffect } from "react";
import CircularProgress from "@mui/material/CircularProgress";
import "../styles/PatientCases.css";
import CaseDetail from "./CaseDetail";
import { PatientCase } from "../services/api";

interface PatientCasesState {
  cases: PatientCase[];
  selectedCase: PatientCase | null;
  loading: boolean;
  error: string | null;
}

const PatientCases: React.FC = () => {
  const [state, setState] = useState<PatientCasesState>({
    cases: [],
    selectedCase: null,
    loading: false,
    error: null,
  });

  const [searchTerm, setSearchTerm] = useState("");

  useEffect(() => {
    fetchCases();
  }, []);

  const fetchCases = async () => {
    setState((prev) => ({ ...prev, loading: true, error: null }));
    try {
      const response = await fetch(
        `${process.env.REACT_APP_API_URL || "http://localhost:8080/api/v1"}/cases`,
      );
      if (!response.ok) throw new Error("Failed to fetch cases");
      const data = await response.json();
      setState((prev) => ({
        ...prev,
        cases: data,
        selectedCase: data.length > 0 ? data[0] : null,
        loading: false,
      }));
    } catch (error) {
      setState((prev) => ({
        ...prev,
        error: error instanceof Error ? error.message : "An error occurred",
        loading: false,
      }));
    }
  };

  const handleCaseSelect = (caseItem: PatientCase) => {
    setState((prev) => ({ ...prev, selectedCase: caseItem }));
  };

  const filteredCases = state.cases.filter((caseItem) =>
    caseItem.caseTitle.toLowerCase().includes(searchTerm.toLowerCase()),
  );

  return (
    <div className="patient-cases-container">
      {/* Sidebar */}
      <div className="cases-sidebar">
        <div className="sidebar-header">
          <h2>Patient Cases</h2>
          <span className="case-count">{filteredCases.length}</span>
        </div>

        {/* Search Bar */}
        <div className="search-box">
          <input
            type="text"
            placeholder="🔍 Search cases..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
        </div>

        {/* Cases List */}
        <div className="cases-list">
          {state.loading ? (
            <div className="loading-container">
              <CircularProgress size={40} />
              <p>Loading cases...</p>
            </div>
          ) : state.error ? (
            <div className="error-container">
              <p className="error-message">⚠️ {state.error}</p>
              <button className="btn-retry" onClick={fetchCases}>
                Retry
              </button>
            </div>
          ) : filteredCases.length === 0 ? (
            <div className="empty-container">
              <p className="empty-message">📋 No cases found</p>
              <small>Create a new case to get started</small>
            </div>
          ) : (
            filteredCases.map((caseItem) => (
              <div
                key={caseItem.id}
                className={`case-item ${state.selectedCase?.id === caseItem.id ? "active" : ""}`}
                onClick={() => handleCaseSelect(caseItem)}
              >
                <div className="case-item-header">
                  <div className="case-title-badge">{caseItem.caseTitle}</div>
                  <span className="case-status-badge">
                    {caseItem.summary ? "✓" : "⏳"}
                  </span>
                </div>
                <div className="case-item-meta">
                  <span className="case-age">Age: {caseItem.patientAge}</span>
                  <span className="case-gender">{caseItem.gender}</span>
                </div>
                {caseItem.summary &&
                  caseItem.summary.confidenceScore !== undefined && (
                    <div className="case-confidence">
                      <div className="confidence-bar">
                        <div
                          className="confidence-fill"
                          style={{
                            width: `${caseItem.summary.confidenceScore}%`,
                          }}
                        ></div>
                      </div>
                      <small>
                        {caseItem.summary.confidenceScore}% confidence
                      </small>
                    </div>
                  )}
              </div>
            ))
          )}
        </div>

        {/* Refresh Button */}
        <div className="sidebar-footer">
          <button
            className="btn-refresh"
            onClick={fetchCases}
            disabled={state.loading}
          >
            🔄 Refresh
          </button>
        </div>
      </div>

      {/* Main Panel */}
      <div className="cases-main-panel">
        {state.selectedCase ? (
          <CaseDetail
            caseItem={state.selectedCase}
            onCaseUpdated={() => fetchCases()}
          />
        ) : (
          <div className="no-selection-container">
            <div className="no-selection-icon">📋</div>
            <h2>No Case Selected</h2>
            <p>Select a case from the sidebar to view details and summarize</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default PatientCases;
