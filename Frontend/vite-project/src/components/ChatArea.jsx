// src/components/ChatArea.jsx

import { useEffect, useRef } from "react";
import Message from "./Message";

export default function ChatArea({ messages }) {
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages]);

  return (
    <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-3">
      {messages.map((msg, index) => (
        <Message
          key={index}
          role={msg.role}
          content={msg.content}
        />
      ))}

      <div ref={chatEndRef} />
    </div>
  );
}