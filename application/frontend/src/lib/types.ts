export interface Message {
  id: string;
  content: string;
  role: "system" | "user" | "assistant" | "function" | "data" | "tool";
  major?: string
}

export interface Chat extends Record<string, any> {
  id: string
  title: string
  createdAt: Date
  userId: string
  message: Message[]
}