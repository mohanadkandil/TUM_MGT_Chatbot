import { cn } from "@/lib/utils";
import { ChatPanel } from "./chat-panel";
import { useChat } from "ai/react";
import { useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { useLocalStorage } from "@/lib/hooks/use-local-storage";
import { Message } from "ai";
import { ChatList } from "./chat-list";
import { EmptyScreen } from "./empty-screen";
import { QuestionsRecommendation } from "./questions-recommendation";

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
      <div className={cn("pb-[200px] pt-4 md:pt-10", className)}>
        {messages.length ? (
          <>
            <ChatList messages={messages} />
          </>
        ) : (
          <>
            <div className="mx-auto max-w-5xl py-12">
              <h1 className="text-[#3070B3] font-extrabold text-5xl">
                Hello Penny
              </h1>
              <p className="pt-4 text-slate-600 text-xl">
                Ask TUM-specific questions here. Get quick answers on courses,
                admin, and more.
              </p>
            </div>
            <QuestionsRecommendation />
          </>
        )}
      </div>
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
