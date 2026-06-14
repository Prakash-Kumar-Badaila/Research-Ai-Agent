// src/hooks/useChat.js

import { useState } from "react";
import { streamResponse } from "../services/api";

export default function useChat() {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const sendMessage = async (input) => {
    if (!input.trim()) return;

    setLoading(true);

    setMessages((prev) => [
      ...prev,
      { role: "user", content: input },
      { role: "ai", content: "" },
    ]);

    try {
      await streamResponse(input, (result) => {
        setMessages((prev) => {
          const updated = [...prev];

          updated[updated.length - 1] = {
            ...updated[updated.length - 1],
            content: result,
          };

          return updated;
        });
      });
    } catch (error) {
      console.error(error);
    }

    setLoading(false);
  };

  return {
    messages,
    loading,
    sendMessage,
  };
}