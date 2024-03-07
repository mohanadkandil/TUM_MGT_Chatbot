"use client";

import { useLocalStorage } from "@/lib/hooks/use-local-storage";
import { SidebarItems } from "./sidebar-items";
import { Chat } from "@/lib/types";
import { SettingsDialog } from "../settings-dialog";

export async function SidebarList() {
  const [chats, _] = useLocalStorage<Record<string, Chat>>("chats", {});

  // Convert chats object into an array of chat objects
  const chatsArray = Object.keys(chats).map((key) => ({
    chatId: key, // Renamed to avoid conflict
    ...chats[key],
  }));

  // Now, pass chatsArray to SidebarItems

  return (
    <div className="flex flex-1 flex-col overflow-hidden">
      <div className="flex-1 overflow-auto">
        {chatsArray?.length ? (
          <div className="space-y-2 px-2">
            <SidebarItems chats={chatsArray} />
          </div>
        ) : (
          <div className="p-8 text-center">
            <p className="text-sm text-muted-foreground">No chat history</p>
          </div>
        )}
      </div>
      <div className="flex items-center justify-between p-4">
        <div className="flex items-center gap-4">
          <div className="w-8 h-8 rounded-full bg-slate-300" />
          <span className="text-sm font-medium">TUM User</span>
        </div>
        <SettingsDialog />
      </div>
    </div>
  );
}
