import { useState } from "react";

function App() {
  const [input, setInput] = useState("");
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);

  const startStream = async () => {
    if (!input.trim()) return;

    setText("");
    setLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:8000/ai_call/", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: new URLSearchParams({
          query: input,
        }),
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      let result = "";

      while (true) {
        const { value, done } = await reader.read();

        if (done) break;

        result += decoder.decode(value);
        setText(result);
      }
    } catch (error) {
      console.error(error);
      setText("Error connecting to server.");
    }

    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center px-4">
      <div className="w-full max-w-2xl bg-white rounded-2xl shadow-lg p-6">

        <h1 className="text-2xl font-bold text-center mb-6">
          AI Research Agent
        </h1>

        <div className="flex gap-2 mb-4">
          <input
            type="text"
            placeholder="Ask something..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            className="flex-1 border rounded-lg px-4 py-2 outline-none"
          />

          <button
            onClick={startStream}
            disabled={loading}
            className="bg-blue-600 text-white px-5 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? "Thinking..." : "Send"}
          </button>
        </div>

        <div className="border rounded-lg p-4 min-h-[200px] bg-gray-50">
          <pre className="whitespace-pre-wrap text-gray-800">
            {text || "Response will appear here..."}
          </pre>
        </div>

      </div>
    </div>
  );
}

export default App;