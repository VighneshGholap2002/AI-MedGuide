import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/CaseForm.css";
import { PatientCase, caseService } from "../services/api";

const CaseForm: React.FC = () => {
  const navigate = useNavigate();

  const [formData, setFormData] = useState<Partial<PatientCase>>({
    caseTitle: "",
    patientAge: "",
    gender: "",
    clinicalNotes: "",
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
    >,
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
    setError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setLoading(true);
      setError(null);

      // Validation
      if (
        !formData.caseTitle ||
        !formData.patientAge ||
        !formData.gender ||
        !formData.clinicalNotes
      ) {
        setError("All fields are required");
        setLoading(false);
        return;
      }

      await caseService.createCase(formData as PatientCase);

      setSuccess(true);
      setFormData({
        caseTitle: "",
        patientAge: "",
        gender: "",
        clinicalNotes: "",
      });

      // Redirect after 2 seconds
      setTimeout(() => {
        navigate("/patient-cases");
      }, 2000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create case");
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setFormData({
      caseTitle: "",
      patientAge: "",
      gender: "",
      clinicalNotes: "",
    });
    setError(null);
    setSuccess(false);
  };

  return (
    <div className="create-case-container">
      <div className="form-wrapper">
        <div className="form-header">
          <h1>Create New Patient Case</h1>
          <p>
            Enter patient information and clinical notes to create a new case
            for analysis
          </p>
        </div>

        {success && (
          <div className="success-tooltip">
            ✓ Case created successfully! Redirecting...
          </div>
        )}

        {error && (
          <div className="error-message">
            <span className="error-icon">⚠️</span>
            <div>
              <h3>Error</h3>
              <p>{error}</p>
            </div>
          </div>
        )}

        <form onSubmit={handleSubmit} className="form-content">
          <div className="form-section">
            <h3>Patient Information</h3>

            <div className="form-group">
              <label htmlFor="caseTitle">Case Title *</label>
              <input
                type="text"
                id="caseTitle"
                name="caseTitle"
                value={formData.caseTitle || ""}
                onChange={handleChange}
                placeholder="e.g., Acute Chest Pain - 65-year-old Male"
                required
                maxLength={200}
              />
              <small>Maximum 200 characters</small>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="patientAge">Patient Age *</label>
                <input
                  type="number"
                  id="patientAge"
                  name="patientAge"
                  value={formData.patientAge || ""}
                  onChange={handleChange}
                  placeholder="e.g., 65"
                  min="0"
                  max="150"
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="gender">Gender *</label>
                <select
                  id="gender"
                  name="gender"
                  value={formData.gender || ""}
                  onChange={handleChange}
                  required
                >
                  <option value="">-- Select Gender --</option>
                  <option value="Male">Male</option>
                  <option value="Female">Female</option>
                  <option value="Other">Other</option>
                </select>
              </div>
            </div>
          </div>

          <div className="form-section">
            <h3>Clinical Notes</h3>

            <div className="form-group">
              <label htmlFor="clinicalNotes">Clinical Notes *</label>
              <textarea
                id="clinicalNotes"
                name="clinicalNotes"
                value={formData.clinicalNotes || ""}
                onChange={handleChange}
                placeholder="Paste clinical notes here. Include sections like Chief Complaint, History of Present Illness, Physical Examination, Assessment, and Plan for best results..."
                required
                rows={10}
              />
              <small>
                {formData.clinicalNotes?.length || 0} / 10000 characters
              </small>
            </div>
          </div>

          <div className="form-actions">
            <button
              type="button"
              className="btn btn-secondary"
              onClick={handleReset}
              disabled={loading}
            >
              Clear Form
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={loading}
            >
              {loading ? (
                <>
                  <span className="spinner"></span>
                  Creating Case...
                </>
              ) : (
                <>
                  <span>➕</span>
                  Create Case
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CaseForm;
