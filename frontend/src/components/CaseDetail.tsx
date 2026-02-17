import React, { useState } from "react";
import CircularProgress from "@mui/material/CircularProgress";
import "../styles/CaseDetail.css";
import { PatientCase } from "../services/api";

interface CaseDetailProps {
  caseItem: PatientCase;
  onCaseUpdated: () => void;
}

const CaseDetail: React.FC<CaseDetailProps> = ({ caseItem, onCaseUpdated }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [localCase, setLocalCase] = useState(caseItem);

  const handleSummarize = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(
        `${process.env.REACT_APP_API_URL || "http://localhost:8080/api/v1"}/cases/${localCase.id}/summarize`,
        { method: "POST" },
      );

      if (!response.ok) throw new Error("Failed to summarize case");

      const data = await response.json();
      setLocalCase(data);
      onCaseUpdated();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to summarize case");
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteCase = async () => {
    if (!window.confirm("Are you sure you want to delete this case?")) {
      return;
    }

    try {
      const response = await fetch(
        `${process.env.REACT_APP_API_URL || "http://localhost:8080/api/v1"}/cases/${localCase.id}`,
        { method: "DELETE" },
      );

      if (!response.ok) throw new Error("Failed to delete case");
      onCaseUpdated();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete case");
    }
  };

  return (
    <div className="case-detail-container">
      {/* Case Header */}
      <div className="case-detail-header">
        <div>
          <h2>{localCase.caseTitle}</h2>
          <div className="case-meta">
            <span className="meta-item">👤 Age: {localCase.patientAge}</span>
            <span className="meta-item">⚧ Gender: {localCase.gender}</span>
          </div>
        </div>
        <button
          className="btn-delete"
          onClick={handleDeleteCase}
          title="Delete case"
        >
          🗑️
        </button>
      </div>

      {/* Error Message */}
      {error && (
        <div className="error-message">
          <span>⚠️</span>
          <p>{error}</p>
          <button onClick={() => setError(null)}>✕</button>
        </div>
      )}

      {/* Clinical Notes Section */}
      <div className="section">
        <h3>Clinical Notes</h3>
        <div className="clinical-notes">{localCase.clinicalNotes}</div>
      </div>

      {/* Summarize Button */}
      {!localCase.summary && (
        <div className="section no-summary">
          <div className="no-summary-content">
            <div className="no-summary-icon">📊</div>
            <h3>Case Not Yet Summarized</h3>
            <p>Click the button below to generate an AI-powered summary</p>
          </div>
          <button
            className={`btn btn-summarize ${isLoading ? "loading" : ""}`}
            onClick={handleSummarize}
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <CircularProgress size={20} />
                Summarizing...
              </>
            ) : (
              <>✨ Summarize Case</>
            )}
          </button>
        </div>
      )}

      {/* Summary Results */}
      {localCase.summary && (
        <div className="summary-results">
          <div className="summary-header">
            <h3>Summarization Results</h3>
            <button
              className="btn btn-resummarize"
              onClick={handleSummarize}
              disabled={isLoading}
            >
              🔄 Re-Summarize
            </button>
          </div>

          {/* Chief Complaint */}
          <div className="summary-section">
            <h4>Chief Complaint</h4>
            <p className="summary-text">{localCase.summary.chiefComplaint}</p>
          </div>

          {/* Key Findings */}
          <div className="summary-section">
            <h4>Key Findings</h4>
            <p className="summary-text">{localCase.summary.keyFindings}</p>
          </div>

          {/* Assessment */}
          <div className="summary-section">
            <h4>Assessment</h4>
            <p className="summary-text">{localCase.summary.assessment}</p>
          </div>

          {/* Risk Words */}
          {localCase.summary?.riskWords &&
            localCase.summary.riskWords.length > 0 && (
              <div className="summary-section risk-section">
                <h4>⚠️ Risk Words Detected</h4>
                <div className="risk-words">
                  {localCase.summary.riskWords.map((risk, idx) => (
                    <span
                      key={idx}
                      className={`risk-badge ${typeof risk === "object" && risk.level ? risk.level.toLowerCase() : "high"}`}
                    >
                      {typeof risk === "object" ? risk.word : risk}
                      {typeof risk === "object" && risk.level && (
                        <small>{risk.level}</small>
                      )}
                    </span>
                  ))}
                </div>
              </div>
            )}

          {/* Risk Factors */}
          {localCase.summary?.riskFactors &&
            localCase.summary.riskFactors.length > 0 && (
              <div className="summary-section">
                <h4>Risk Factors</h4>
                <ul className="risk-factors">
                  {localCase.summary.riskFactors.map((factor, idx) => (
                    <li key={idx}>
                      <span className="risk-icon">⚠️</span>
                      {factor}
                    </li>
                  ))}
                </ul>
              </div>
            )}

          {/* Recommendations */}
          <div className="summary-section">
            <h4>Recommendations</h4>
            <ol className="recommendations">
              {localCase.summary.recommendations.map((rec, idx) => (
                <li key={idx}>{rec}</li>
              ))}
            </ol>
          </div>

          {/* ICD Codes */}
          <div className="summary-section">
            <h4>ICD Codes</h4>
            <div className="icd-codes">{localCase.summary.icdCodes}</div>
          </div>

          {/* Confidence Score */}
          {(localCase.summary?.confidenceScore !== undefined ||
            localCase.summary?.confidenceScore !== null) && (
            <div className="summary-section confidence-section">
              <h4>Confidence Score</h4>
              <div className="confidence-display">
                <div className="confidence-bar-container">
                  <div className="confidence-bar">
                    <div
                      className="confidence-fill"
                      style={{
                        width: `${localCase.summary.confidenceScore || 0}%`,
                      }}
                    ></div>
                  </div>
                  <span className="confidence-text">
                    {localCase.summary.confidenceScore || 0}%
                  </span>
                </div>
                <p className="confidence-note">
                  Higher scores indicate better quality analysis
                </p>
              </div>
            </div>
          )}

          {/* Metadata */}
          {localCase.summary?.metadata && (
            <div className="summary-section metadata-section">
              <h4>Analysis Details</h4>
              <div className="metadata">
                <div className="metadata-item">
                  <span>Processed:</span>
                  <span>
                    {new Date(
                      localCase.summary.metadata.processedAt,
                    ).toLocaleString()}
                  </span>
                </div>
                <div className="metadata-item">
                  <span>Processing Time:</span>
                  <span>{localCase.summary.metadata.processingTimeMs}ms</span>
                </div>
                <div className="metadata-item">
                  <span>Model Version:</span>
                  <span>{localCase.summary.metadata.modelVersion}</span>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default CaseDetail;
