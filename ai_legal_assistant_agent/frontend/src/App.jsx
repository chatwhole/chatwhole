import React, { useState } from "react";

function App() {
  const [contractText, setContractText] = useState("");
  const [jurisdiction, setJurisdiction] = useState("");
  const [review, setReview] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleReview = async () => {
    setLoading(true);
    try {
      const response = await fetch("http://localhost:8000/api/contract_review", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ contract_text: contractText, jurisdiction }),
      });
      const data = await response.json();
      setReview(data.review);
    } catch (error) {
      setReview({ error: "Error fetching contract review." });
    }
    setLoading(false);
  };

  return (
    <div className="max-w-3xl mx-auto p-4 border rounded shadow mt-10">
      <h1 className="text-xl font-bold mb-4">AI Legal Assistant Agent</h1>
      <div className="mb-4">
        <label className="block mb-1">Contract Clause Text:</label>
        <textarea
          rows={6}
          value={contractText}
          onChange={(e) => setContractText(e.target.value)}
          className="w-full border rounded px-3 py-2"
        />
      </div>
      <div className="mb-4">
        <label className="block mb-1">Jurisdiction:</label>
        <input
          type="text"
          value={jurisdiction}
          onChange={(e) => setJurisdiction(e.target.value)}
          className="w-full border rounded px-3 py-2"
        />
      </div>
      <button
        onClick={handleReview}
        disabled={loading}
        className="bg-blue-600 text-white px-4 py-2 rounded"
      >
        {loading ? "Reviewing..." : "Review Contract"}
      </button>
      {review && (
        <div className="mt-4 p-3 border rounded bg-gray-100">
          {review.error ? (
            <p className="text-red-600">{review.error}</p>
          ) : (
            <>
              <h2 className="font-semibold">Flags:</h2>
              <ul className="list-disc list-inside">
                {review.flags.map((flag, idx) => (
                  <li key={idx}>{flag}</li>
                ))}
              </ul>
              <h2 className="font-semibold mt-2">Suggestions:</h2>
              <ul className="list-disc list-inside">
                {review.suggestions.map((suggestion, idx) => (
                  <li key={idx}>{suggestion}</li>
                ))}
              </ul>
              <h2 className="font-semibold mt-2">Explanation:</h2>
              <p>{review.explanation}</p>
            </>
          )}
        </div>
      )}
    </div>
  );
}

export default App;
