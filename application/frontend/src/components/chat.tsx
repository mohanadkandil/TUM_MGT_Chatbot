"use client";
import { cn } from "@/lib/utils";
import { UseChatHelpers } from "ai/react";
import { FormEvent, useEffect, useRef, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { useLocalStorage } from "@/lib/hooks/use-local-storage";
import { ChatList } from "./chat-list";
import axios, { AxiosError } from "axios";
import { dataTagSymbol, useMutation } from "@tanstack/react-query";
import { QuestionsRecommendation } from "./questions-recommendation";
import { ButtonScrollToBottom } from "./button-scroll-to-bottom";
import { Tooltip, TooltipContent, TooltipTrigger } from "./ui/tooltip";
import Textarea from "react-textarea-autosize";
import { IconSend } from "./icons";
import { useEnterSubmit } from "@/lib/hooks/use-enter-submit";
import { Button, buttonVariants } from "@/components/ui/button";
import { useToast } from "./ui/use-toast";
import { Message } from "@/lib/types";

export interface ChatProps extends React.ComponentProps<"div"> {
  initialMessages?: Message[];
  id?: string;
}

export interface PormptProps
  extends Pick<UseChatHelpers, "input" | "setInput"> {
  onSubmit: (value: string) => void;
  isLoading: boolean;
}

export function Chat({ id, initialMessages = [] }: ChatProps) {
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
  const { toast } = useToast();
  const { formRef, onKeyDown } = useEnterSubmit();
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const router = useRouter();
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [input, setInput] = useState<string>("");
  const isLoadingRef = useRef(false);
  const initialMessagesRef = useRef(initialMessages);

  const { mutate: sendMessage, isPending: isMessagePending } = useMutation({
    mutationFn: async () => {
      const payload = JSON.stringify({ data: input });
      const { data } = await axios.post("api/chat", payload);
      return data.answer.answer;
    },
    onError: (err) => {
      console.log(err);
      return toast({
        title: "There was a problem.",
        description: "Something went wrong. Please try again.",
        variant: "destructive",
      });
    },
    onSuccess: (data) => {
      console.log(data);
      const newMessage: Message = {
        id: Date.now().toString(),
        content: data,
        role: "system", // or 'system', directly using the string literal
      };
      setMessages((prevMessages) => [...prevMessages, newMessage]);
      addNewMessageToChats(newMessage, id);
    },
  });

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    const newMessage: Message = {
      id: Date.now().toString(),
      content: input,
      role: "user", // or 'system', directly using the string literal
    };
    isLoadingRef.current = true;
    setMessages((prevMessages) => [...prevMessages, newMessage]);
    addNewMessageToChats(newMessage, id);
    setInput("");

    sendMessage();
  };

  const addNewMessageToChats = (
    newMessage: Message,
    chatId: string | number | undefined
  ) => {
    const chats = JSON.parse(localStorage.getItem("chats") || "{}");
    if (chatId) {
      const chatMessages = chats[chatId] || [];
      chatMessages.push(newMessage);
      chats[chatId] = chatMessages;
    }
    localStorage.setItem("chats", JSON.stringify(chats));
  };
  useEffect(() => {
    if (
      JSON.stringify(initialMessages) !==
      JSON.stringify(initialMessagesRef.current)
    ) {
      setMessages(initialMessages);
      initialMessagesRef.current = initialMessages;
    }
  }, [initialMessages]);

  return (
    <>
      <div className={cn("pb-[200px] pt-4 md:pt-10")}>
        {messages.length ? (
          <>
            <ChatList messages={messages} />
          </>
        ) : (
          <>
            <div className="mx-auto max-w-5xl py-12 px-12 md:px-8">
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
            {isMessagePending ? (
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
            <form onSubmit={handleSubmit} ref={formRef}>
              <div className="relative flex flex-col w-full px-8 overflow-hidden max-h-60 grow bg-background sm:border sm:rounded-2xl sm:px-4">
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
                <div className="absolute right-8 top-3.5 sm:right-4">
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <Button
                        type="submit"
                        variant="ghost"
                        size="icon"
                        disabled={isMessagePending || input === ""}
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
