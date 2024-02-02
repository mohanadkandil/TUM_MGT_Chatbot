"use client";

import { Chat } from "@/components/chat";

export default function Home() {
  return (
    <section className="h-screen flex-col flex items-center justify-center gap-3">
      <Chat />
    </section>
  );
}
