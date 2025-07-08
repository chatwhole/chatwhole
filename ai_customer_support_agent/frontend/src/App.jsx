import React, { useState } from "react";

function App() {
  const [messages, setMessages] = useState([
    { from: "bot", text: "Hello! How can I assist you today?" },
  ]);
  const [input, setInput] = useState("");

  const sendMessage = async () => {
    if (!input.trim()) return;
    const userMessage = { from: "user", text: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");

    try {
      const response = await fetch("http://localhost:8000/api/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: input }),
      });
      const data = await response.json();
      const botMessage = { from: "bot", text: data.answer };
      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      const errorMessage = {
        from: "bot",
        text: "Sorry, there was an error processing your request.",
      };
      setMessages((prev) => [...prev, errorMessage]);
    }
  };

  return (
    <div className="max-w-md mx-auto p-4 border rounded shadow mt-10">
      <h1 className="text-xl font-bold mb-4">AI Customer Support Chat</h1>
      <div className="h-64 overflow-y-auto border p-2 mb-4">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`mb-2 ${
              msg.from === "user" ? "text-right" : "text-left"
            }`}
          >
            <span
              className={`inline-block px-3 py-1 rounded ${
                msg.from === "user" ? "bg-blue-500 text-white" : "bg-gray-300"
              }`}
            >
              {msg.text}
            </span>
          </div>
        ))}
      </div>
      <div className="flex">
        <input
          className="flex-grow border rounded-l px-3 py-2"
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          placeholder="Type your message..."
        />
        <button
          className="bg-blue-600 text-white px-4 rounded-r"
          onClick={sendMessage}
        >
          Send
        </button>
      </div>
    </div>
  );
}

export default App;
