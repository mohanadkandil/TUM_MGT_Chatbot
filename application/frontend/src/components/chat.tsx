import { cn } from "@/lib/utils";
import { UseChatHelpers } from "ai/react";
import { FormEvent, useRef, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { useLocalStorage } from "@/lib/hooks/use-local-storage";
import { Message } from "ai";
import { ChatList } from "./chat-list";
import { EmptyScreen } from "./empty-screen";
import { QuestionsRecommendation } from "./questions-recommendation";
import { ButtonScrollToBottom } from "./button-scroll-to-bottom";
import { Tooltip, TooltipContent, TooltipTrigger } from "./ui/tooltip";
import Textarea from "react-textarea-autosize";
import { IconPlus, IconSend } from "./icons";
import { useEnterSubmit } from "@/lib/hooks/use-enter-submit";
import { Button, buttonVariants } from "@/components/ui/button";

export interface ChatProps extends React.ComponentProps<"div"> {
  initialMessages?: Message[];
  id?: string;
}
export interface PormptProps
  extends Pick<UseChatHelpers, "input" | "setInput"> {
  onSubmit: (value: string) => void;
  isLoading: boolean;
}

interface SimplifiedMessage {
  id: string;
  content: string;
  role: "system" | "user" | "assistant" | "function" | "data" | "tool";
}

export function Chat() {
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

  const { formRef, onKeyDown } = useEnterSubmit();
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const router = useRouter();
  const [messages, setMessages] = useState<SimplifiedMessage[]>([]);
  const [input, setInput] = useState<string>("");
  const isLoadingRef = useRef(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    const newMessage: SimplifiedMessage = {
      id: Date.now().toString(),
      content: input,
      role: "user", // or 'system', directly using the string literal
    };
    isLoadingRef.current = true;
    setMessages((prevMessages) => [...prevMessages, newMessage]);
    setInput("");

    const encodedQuestion = encodeURIComponent(input);
    const url = `${process.env.NEXT_PUBLIC_CONVERSATIONAPI}/conversation?question=${encodedQuestion}`;

    try {
      const response = await fetch(url, {
        method: "POST",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          conversation: [
            {
              role: "string", // Adjust the role as needed for your application
              content: input,
            },
          ],
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      const newMessage: SimplifiedMessage = {
        id: Date.now().toString(),
        content: data.answer.answer,
        role: "system", // or 'system', directly using the string literal
      };
      setMessages((prevMessages) => [...prevMessages, newMessage]);
      isLoadingRef.current = false;
      // Handle success response here, such as updating UI or state accordingly
    } catch (error) {
      console.error("Error submitting question:", error);
      // Handle error scenario, such as displaying an error message to the user
    }
  };
  return (
    <>
      <div className={cn("pb-[200px] pt-4 md:pt-10")}>
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
      <div className="fixed inset-x-0 bottom-0 w-full animate-in duration-300 ease-in-out peer-[[data-state=open]]:group-[]:lg:pl-[250px] peer-[[data-state=open]]:group-[]:xl:pl-[300px]">
        <ButtonScrollToBottom />
        <div className="mx-auto sm:max-w-2xl sm:px-4">
          <div className="flex items-center justify-center h-12">
            {isLoadingRef.current ? (
              <Button
                variant="outline"
                onClick={() => stop()}
                className="bg-background"
              >
                Generating ...
              </Button>
            ) : null}
          </div>
        </div>
        <div className="mx-auto sm:max-w-2xl sm:px-4">
          <div className="px-4 py-2 space-y-4 md:py-4">
            <form onSubmit={handleSubmit}>
              <div className="relative flex flex-col w-full px-8 overflow-hidden max-h-60 grow bg-background sm:border sm:rounded-2xl sm:px-12">
                <Tooltip>
                  <TooltipTrigger asChild>
                    <button
                      onClick={(e) => {
                        e.preventDefault();
                        router.refresh();
                        router.push("/chat");
                      }}
                      className={cn(
                        buttonVariants({ size: "sm", variant: "outline" }),
                        "absolute left-0 top-4 size-8 rounded-full bg-background p-0 sm:left-4"
                      )}
                    >
                      <IconPlus />
                      <span className="sr-only">New Chat</span>
                    </button>
                  </TooltipTrigger>
                  <TooltipContent>New Chat</TooltipContent>
                </Tooltip>
                <Textarea
                  ref={inputRef}
                  tabIndex={0}
                  onKeyDown={onKeyDown}
                  rows={1}
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Message TUM.Chat"
                  spellCheck={false}
                  className="min-h-[60px] w-full resize-none bg-transparent px-4 py-[1.3rem] focus-within:outline-none sm:text-sm"
                />
                <div className="absolute right-0 top-3.5 sm:right-4">
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <Button
                        type="submit"
                        variant="ghost"
                        size="icon"
                        disabled={isLoadingRef.current || input === ""}
                      >
                        <IconSend />
                        <span className="sr-only">Send message</span>
                      </Button>
                    </TooltipTrigger>
                    <TooltipContent>Send message</TooltipContent>
                  </Tooltip>
                </div>
              </div>
            </form>
          </div>
        </div>
      </div>
    </>
  );
}
