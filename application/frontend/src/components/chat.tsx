"use client";

import { cn } from "@/lib/utils";
import { UseChatHelpers } from "ai/react";
import {
  FormEvent,
  SetStateAction,
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";
import { useLocalStorage } from "@/lib/hooks/use-local-storage";
import { ChatList } from "./chat-list";
import { QuestionsRecommendation } from "./questions-recommendation";
import { ButtonScrollToBottom } from "./button-scroll-to-bottom";
import { Tooltip, TooltipContent, TooltipTrigger } from "./ui/tooltip";
import Textarea from "react-textarea-autosize";
import { IconSend } from "./icons";
import { useEnterSubmit } from "@/lib/hooks/use-enter-submit";
import { Button } from "@/components/ui/button";
import { useToast } from "./ui/use-toast";
import { Message } from "@/lib/types";
import { useStreamResponse } from "@/lib/hooks/use-stream-response";

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
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [input, setInput] = useState<string>("");
  const isLoadingRef = useRef(false);
  const initialMessagesRef = useRef(initialMessages);
  const [streamingMessageId, setStreamingMessageId] = useState<string | null>(
    null
  );

  const addOrUpdateMessageInChats = (
    messageToUpdate: Message,
    chatId: string | number
  ) => {
    const chats = JSON.parse(localStorage.getItem("chats") || "{}");
    if (!chats[chatId]) chats[chatId] = [];
    const messageIndex = chats[chatId].findIndex(
      (message: { id: string }) => message.id === messageToUpdate.id
    );

    if (messageIndex >= 0) {
      chats[chatId][messageIndex] = messageToUpdate; // Update existing message
    } else {
      chats[chatId].push(messageToUpdate); // Add new message
    }

    localStorage.setItem("chats", JSON.stringify(chats));
  };

  const handleStreamedText = useCallback(
    (newText: SetStateAction<string>) => {
      setMessages((currentMessages) => {
        const updatedMessages = currentMessages.map((msg) => {
          if (msg.id === streamingMessageId) {
            const updatedMessage = { ...msg, content: msg.content + newText };
            // Persist the updated message
            if (id !== undefined) {
              addOrUpdateMessageInChats(updatedMessage, id);
            }
            return updatedMessage;
          }
          return msg;
        });
        return updatedMessages;
      });
    },
    [streamingMessageId, id]
  );

  const {
    startStream,
    isLoading: isMessageLoading,
    isTriggerFeedback,
  } = useStreamResponse({
    streamCallback: handleStreamedText,
  });

  const startStreamWithSetup = () => {
    const streamingMessageId = `system-${Date.now().toString()}`; // Generate a unique ID for the streaming message
    const newMessage: Message = {
      id: streamingMessageId,
      content: "", // Initialize with empty content
      role: "system",
    };
    setMessages((prev) => [...prev, newMessage]); // Add the new system message to the chat
    setStreamingMessageId(streamingMessageId); // Save this ID to update the message later

    // Assuming startStream is a function that begins the text streaming process
    startStream(input); // Pass any necessary input to start the stream
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    const newMessage: Message = {
      id: `user-${Date.now().toString()}`,
      content: input,
      role: "user", // or 'system', directly using the string literal
    };
    isLoadingRef.current = true;
    setMessages((prevMessages) => [...prevMessages, newMessage]);
    addOrUpdateMessageInChats(newMessage, id as string);
    startStreamWithSetup();
    setInput("");
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
            <ChatList
              messages={messages}
              isTriggerFeedback={isTriggerFeedback}
            />
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
            {isMessageLoading ? (
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
                  maxLength={1000}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Message TUM.Chat"
                  spellCheck={false}
                  className="min-h-[60px] w-full resize-none bg-transparent pr-28 py-[1.3rem] focus-within:outline-none sm:text-sm"
                />
                <div className="absolute right-8 top-3.5 sm:right-4 flex items-center space-x-2">
                  <span className="text-sm text-gray-500">{`${input.length}/1000`}</span>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <Button
                        type="submit"
                        variant="ghost"
                        size="icon"
                        disabled={isMessageLoading || input === ""}
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
