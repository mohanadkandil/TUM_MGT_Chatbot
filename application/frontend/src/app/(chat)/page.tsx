"use client";
import { Chat } from "@/components/chat";
import { nanoid } from "ai";

export default function IndexPage() {
  const id = nanoid();

  return <Chat id={id} />;
}
