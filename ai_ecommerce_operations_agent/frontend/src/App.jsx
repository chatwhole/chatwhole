import React, { useState } from "react";

function App() {
  const [productName, setProductName] = useState("");
  const [keyFeatures, setKeyFeatures] = useState("");
  const [targetMarket, setTargetMarket] = useState("");
  const [tone, setTone] = useState("");
  const [listing, setListing] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    setLoading(true);
    const featuresArray = keyFeatures.split(",").map((f) => f.trim());
    try {
      const response = await fetch("http://localhost:8000/api/product_listing", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          product_name: productName,
          key_features: featuresArray,
          target_market: targetMarket,
          tone: tone,
        }),
      });
      const data = await response.json();
      setListing(data.listing);
    } catch (error) {
      setListing({ error: "Error generating product listing." });
    }
    setLoading(false);
  };

  return (
    <div className="max-w-md mx-auto p-4 border rounded shadow mt-10">
      <h1 className="text-xl font-bold mb-4">AI E-commerce Operations Agent</h1>
      <div className="mb-4">
        <label className="block mb-1">Product Name:</label>
        <input
          type="text"
          value={productName}
          onChange={(e) => setProductName(e.target.value)}
          className="w-full border rounded px-3 py-2"
        />
      </div>
      <div className="mb-4">
        <label className="block mb-1">Key Features (comma separated):</label>
        <input
          type="text"
          value={keyFeatures}
          onChange={(e) => setKeyFeatures(e.target.value)}
          className="w-full border rounded px-3 py-2"
        />
      </div>
      <div className="mb-4">
        <label className="block mb-1">Target Market:</label>
        <input
          type="text"
          value={targetMarket}
          onChange={(e) => setTargetMarket(e.target.value)}
          className="w-full border rounded px-3 py-2"
        />
      </div>
      <div className="mb-4">
        <label className="block mb-1">Tone:</label>
        <input
          type="text"
          value={tone}
          onChange={(e) => setTone(e.target.value)}
          className="w-full border rounded px-3 py-2"
        />
      </div>
      <button
        onClick={handleSubmit}
        disabled={loading}
        className="bg-blue-600 text-white px-4 py-2 rounded"
      >
        {loading ? "Generating..." : "Generate Listing"}
      </button>
      {listing && (
        <div className="mt-4 p-3 border rounded bg-gray-100">
          {listing.error ? (
            <p className="text-red-600">{listing.error}</p>
          ) : (
            <>
              <h2 className="font-semibold">Title:</h2>
              <p>{listing.title}</p>
              <h2 className="font-semibold mt-2">Bullet Points:</h2>
              <ul className="list-disc list-inside">
                {listing.bullet_points.map((point, idx) => (
                  <li key={idx}>{point}</li>
                ))}
              </ul>
              <h2 className="font-semibold mt-2">Description:</h2>
              <p>{listing.description}</p>
              <h2 className="font-semibold mt-2">Meta Keywords:</h2>
              <p>{listing.meta_keywords.join(", ")}</p>
            </>
          )}
        </div>
      )}
    </div>
  );
}

export default App;
