import React, { useState, useEffect } from "react";
import { PatientCase, caseService } from "../services/api";

interface CaseListProps {
  onSelectCase: (caseData: PatientCase) => void;
  refreshTrigger: number;
}

const CaseList: React.FC<CaseListProps> = ({
  onSelectCase,
  refreshTrigger,
}) => {
  const [cases, setCases] = useState<PatientCase[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 5;

  useEffect(() => {
    fetchCases();
  }, [refreshTrigger]);

  const fetchCases = async () => {
    try {
      setLoading(true);
      const response = await caseService.getAllCases();
      // Sort by creation date (newest first)
      const sortedCases = response.data.sort((a, b) => {
        const dateA = new Date(a.createdAt || 0).getTime();
        const dateB = new Date(b.createdAt || 0).getTime();
        return dateB - dateA;
      });
      setCases(sortedCases);
      setCurrentPage(1); // Reset to first page
      setError(null);
    } catch (err) {
      setError("Failed to load cases");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string | undefined) => {
    if (!id) return;
    try {
      await caseService.deleteCase(id);
      setCases(cases.filter((c) => c.id !== id));
    } catch (err) {
      setError("Failed to delete case");
    }
  };

  // Pagination logic
  const totalPages = Math.ceil(cases.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const paginatedCases = cases.slice(startIndex, endIndex);

  const handleNextPage = () => {
    if (currentPage < totalPages) {
      setCurrentPage(currentPage + 1);
    }
  };

  const handlePreviousPage = () => {
    if (currentPage > 1) {
      setCurrentPage(currentPage - 1);
    }
  };

  return (
    <div className="w-full h-full flex flex-col">
      <h2 className="text-2xl font-bold mb-4 text-gray-800">Patient Cases</h2>
      {loading && <p className="text-gray-600">Loading cases...</p>}
      {error && <p className="text-red-600">{error}</p>}

      {/* Scrollable container */}
      <div
        className="flex-1 overflow-y-auto pr-2"
        style={{ maxHeight: "600px" }}
      >
        <div className="grid grid-cols-1 gap-3">
          {paginatedCases.map((caseData) => (
            <div
              key={caseData.id}
              className="p-4 border border-gray-300 rounded-lg hover:shadow-lg cursor-pointer transition bg-white"
            >
              <div className="flex justify-between items-start">
                <div onClick={() => onSelectCase(caseData)} className="flex-1">
                  <h3 className="font-semibold text-lg text-gray-800">
                    {caseData.caseTitle}
                  </h3>
                  <p className="text-sm text-gray-600">
                    Age: {caseData.patientAge} | Gender: {caseData.gender}
                  </p>
                  {caseData.summary?.confidenceScore !== undefined && (
                    <div className="flex items-center gap-2 mt-1">
                      <p className="text-sm text-green-600">
                        Confidence: {caseData.summary.confidenceScore}%
                      </p>
                      {/* Risk indicator */}
                      {caseData.summary?.riskWords &&
                        caseData.summary.riskWords.length > 0 && (
                          <span className="px-2 py-0.5 bg-red-100 text-red-700 text-xs rounded">
                            🚨 High Risk
                          </span>
                        )}
                    </div>
                  )}
                </div>
                <button
                  onClick={() => handleDelete(caseData.id)}
                  className="ml-4 px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600 text-sm"
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
        {cases.length === 0 && !loading && (
          <p className="text-gray-500 text-center py-8">No cases available</p>
        )}
      </div>

      {/* Pagination controls */}
      {cases.length > 0 && (
        <div className="mt-4 flex items-center justify-between border-t pt-4">
          <div className="text-sm text-gray-600">
            Showing {startIndex + 1}-{Math.min(endIndex, cases.length)} of{" "}
            {cases.length} cases
          </div>
          <div className="flex gap-2">
            <button
              onClick={handlePreviousPage}
              disabled={currentPage === 1}
              className="px-4 py-2 bg-gray-300 text-gray-800 rounded hover:bg-gray-400 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              ← Previous
            </button>
            <div className="flex items-center gap-2 px-3">
              <span className="text-sm font-semibold">
                Page {currentPage} of {totalPages}
              </span>
            </div>
            <button
              onClick={handleNextPage}
              disabled={currentPage === totalPages}
              className="px-4 py-2 bg-gray-300 text-gray-800 rounded hover:bg-gray-400 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next →
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default CaseList;
