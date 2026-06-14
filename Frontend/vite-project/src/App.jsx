// src/App.jsx

import Header from "./components/Header";
import ChatArea from "./components/ChatArea";
import ChatInput from "./components/ChatInput";

import useChat from "./hooks/useChat";

function App() {
  const { messages, loading, sendMessage } = useChat();

  return (
    <div className="min-h-screen bg-gray-100 flex justify-center p-4">
      <div className="w-full max-w-4xl h-[90vh] bg-white rounded-2xl shadow-lg flex flex-col">

        <Header />

        <ChatArea messages={messages} />

        <ChatInput
          sendMessage={sendMessage}
          loading={loading}
        />

      </div>
    </div>
  );
}

export default App;