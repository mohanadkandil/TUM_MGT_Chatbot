"use client";
import { Chat } from "@/components/chat";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";

export interface ChatPageProps {
  params: {
    id: string;
  };
}

export default function ChatPage({ params }: ChatPageProps) {
  const id = params.id;
  const [chat, setChat] = useState({ id, messages: [] });

  useEffect(() => {
    // Assuming chats are stored as an object in localStorage under the key "chats"
    const chats = JSON.parse(window.localStorage.getItem("chats") || "{}");
    if (chats[id]) {
      setChat({ id, messages: chats[id] });
      console.log(chats[id]);
      console.log(chats);
    }
  }, [id]);

  console.log(chat.messages);

  return <Chat id={chat.id} initialMessages={chat.messages} />;
}
