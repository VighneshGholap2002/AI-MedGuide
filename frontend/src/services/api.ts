import axios from "axios";

const API_BASE_URL = "http://localhost:8080/api";

interface PatientCase {
  id?: string;
  caseTitle: string;
  patientAge: string;
  gender: string;
  clinicalNotes: string;
  createdAt?: string;
  updatedAt?: string;
  summary?: {
    chiefComplaint: string;
    keyFindings: string;
    assessment: string;
    recommendations: string[];
    icdCodes: string;
    riskWords?: Array<{ word: string; level: string }>;
    riskFactors?: string[];
    confidenceScore?: number;
    metadata?: {
      processedAt: string;
      processingTimeMs: number;
      modelVersion: string;
    };
  };
}

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

export const caseService = {
  createCase: (caseData: PatientCase) =>
    api.post<PatientCase>("/v1/cases", caseData),

  getAllCases: () => api.get<PatientCase[]>("/v1/cases"),

  getCaseById: (id: string) => api.get<PatientCase>(`/v1/cases/${id}`),

  updateCase: (id: string, caseData: PatientCase) =>
    api.put<PatientCase>(`/v1/cases/${id}`, caseData),

  summarizeCase: (id: string) =>
    api.post<PatientCase>(`/v1/cases/${id}/summarize`),

  deleteCase: (id: string) => api.delete(`/v1/cases/${id}`),
};

export type { PatientCase };
