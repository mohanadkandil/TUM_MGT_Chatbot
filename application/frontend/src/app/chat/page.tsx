"use client";
import { ButtonScrollToBottom } from "@/components/button-scroll-to-bottom";
import { Chat } from "@/components/chat";
import { ChatList } from "@/components/chat-list";
import { EmptyScreen } from "@/components/empty-screen";
import { IconSend } from "@/components/icons";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { nanoid } from "ai";
import { useChat } from "ai/react";

export default function IndexPage() {
  const id = nanoid();
  const {
    messages,
    input,
    handleInputChange,
    handleSubmit,
    setInput,
    isLoading,
  } = useChat({ api: "/api/tum-rag" });

  return <Chat id={id} initialMessages={messages} />;
}
