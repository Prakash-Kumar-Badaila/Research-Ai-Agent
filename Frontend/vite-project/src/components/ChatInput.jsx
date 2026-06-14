// src/components/ChatInput.jsx

import { useState } from "react";

export default function ChatInput({ sendMessage, loading }) {
  const [input, setInput] = useState("");

  const handleSubmit = () => {
    sendMessage(input);
    setInput("");
  };

  return (
    <div className="p-4 border-t flex gap-2">
      <input
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Ask something..."
        className="flex-1 border rounded-lg px-4 py-2"
      />

      <button
        onClick={handleSubmit}
        disabled={loading}
        className="bg-blue-600 text-white px-5 py-2 rounded-lg"
      >
        {loading ? "Thinking..." : "Send"}
      </button>
    </div>
  );
}