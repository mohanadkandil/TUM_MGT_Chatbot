import { cn } from "@/lib/utils";
import { ChatPanel } from "./chat-panel";
import { useChat } from "ai/react";
import { useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { useLocalStorage } from "@/lib/hooks/use-local-storage";
import { Message } from "ai";

export interface ChatProps extends React.ComponentProps<"div"> {
  initialMessages?: Message[];
  id?: string;
}

export function Chat({ id, initialMessages, className }: ChatProps) {
  const router = useRouter();
  const path = usePathname();
  const [previewToken, setPreviewToken] = useLocalStorage<string | null>(
    "ai-token",
    null
  );
  const IS_PREVIEW = process.env.VERCEL_ENV === "preview";
  const [previewTokenDialog, setPreviewTokenDialog] = useState(IS_PREVIEW);
  const [previewTokenInput, setPreviewTokenInput] = useState(
    previewToken ?? ""
  );
  const { messages, append, reload, stop, isLoading, input, setInput } =
    useChat({
      initialMessages,
      id,
      body: {
        id,
        previewToken,
      },
      onResponse(response) {
        if (response.status === 401) {
          // toast.error(response.statusText);
        }
      },
      onFinish() {
        if (!path.includes("chat")) {
          window.history.pushState({}, "", `/chat/${id}`);
        }
      },
    });
  return (
    <>
      <ChatPanel
        id={id}
        isLoading={isLoading}
        stop={stop}
        append={append}
        reload={reload}
        messages={messages}
        input={input}
        setInput={setInput}
      />
    </>
  );
}
