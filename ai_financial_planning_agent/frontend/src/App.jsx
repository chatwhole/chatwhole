import React, { useState } from "react";

function App() {
  const [income, setIncome] = useState("");
  const [spending, setSpending] = useState({
    Rent: "",
    Groceries: "",
    Dining: "",
    Travel: "",
    Subscriptions: "",
  });
  const [budgetAdvice, setBudgetAdvice] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSpendingChange = (category, value) => {
    setSpending((prev) => ({ ...prev, [category]: value }));
  };

  const handleSubmit = async () => {
    setLoading(true);
    const spendingNumbers = {};
    for (const key in spending) {
      spendingNumbers[key] = parseFloat(spending[key]) || 0;
    }
    try {
      const response = await fetch("http://localhost:8000/api/budget", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          income: parseFloat(income),
          spending: spendingNumbers,
        }),
      });
      const data = await response.json();
      setBudgetAdvice(data.budget_advice);
    } catch (error) {
      setBudgetAdvice("Error fetching budget advice.");
    }
    setLoading(false);
  };

  return (
    <div className="max-w-md mx-auto p-4 border rounded shadow mt-10">
      <h1 className="text-xl font-bold mb-4">AI Financial Planning Agent</h1>
      <div className="mb-4">
        <label className="block mb-1">Monthly Income ($):</label>
        <input
          type="number"
          value={income}
          onChange={(e) => setIncome(e.target.value)}
          className="w-full border rounded px-3 py-2"
        />
      </div>
      <div className="mb-4">
        <h2 className="font-semibold mb-2">Monthly Spending ($):</h2>
        {Object.keys(spending).map((category) => (
          <div key={category} className="mb-2">
            <label className="block mb-1">{category}:</label>
            <input
              type="number"
              value={spending[category]}
              onChange={(e) => handleSpendingChange(category, e.target.value)}
              className="w-full border rounded px-3 py-2"
            />
          </div>
        ))}
      </div>
      <button
        onClick={handleSubmit}
        disabled={loading}
        className="bg-blue-600 text-white px-4 py-2 rounded"
      >
        {loading ? "Calculating..." : "Get Budget Advice"}
      </button>
      {budgetAdvice && (
        <div className="mt-4 p-3 border rounded bg-gray-100">{budgetAdvice}</div>
      )}
    </div>
  );
}

export default App;
