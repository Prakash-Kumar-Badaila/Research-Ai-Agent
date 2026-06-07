import { useState } from "react";

function App() {
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);

  const startStream = async () => {
    setText("");
    setLoading(true);

    const response = await fetch("http://127.0.0.1:8000/stream/");
    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      setText((prev) => prev + chunk);
    }

    setLoading(false);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 px-4">
      <div className="w-full max-w-xl bg-white shadow-lg rounded-2xl p-6">
        
        <h1 className="text-2xl font-bold text-gray-800 text-center">
          Django Streaming Demo
        </h1>

        <p className="text-gray-500 text-center mt-2">
          Real-time character streaming from backend
        </p>

        <div className="mt-6 flex justify-center">
          <button
            onClick={startStream}
            className="bg-blue-600 hover:bg-blue-700 text-white font-semibold px-6 py-2 rounded-xl transition duration-300 shadow-md"
          >
            {loading ? "Streaming..." : "Start Streaming"}
          </button>
        </div>

        <div className="mt-6 bg-gray-50 border rounded-xl p-4 min-h-[80px]">
          <p className="text-lg text-gray-800 whitespace-pre-wrap">
            {text || "Click start to begin streaming..."}
          </p>
        </div>
      </div>
    </div>
  );
}

export default App;