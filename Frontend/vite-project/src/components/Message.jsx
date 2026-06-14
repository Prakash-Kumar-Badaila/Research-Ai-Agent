// src/components/Message.jsx

export default function Message({ role, content }) {
  return (
    <div
      className={`px-4 py-2 rounded-2xl max-w-[80%] whitespace-pre-wrap ${
        role === "user"
          ? "bg-blue-500 text-white self-end"
          : "bg-gray-200 text-black self-start"
      }`}
    >
      {content}
    </div>
  );
}