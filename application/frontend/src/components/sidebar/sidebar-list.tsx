"use client";

import { useLocalStorage } from "@/lib/hooks/use-local-storage";
import { SidebarItems } from "./sidebar-items";
import { ThemeToggle } from "./theme-toggle";
import { Chat } from "@/lib/types";
import { IconSettings } from "../icons";
import { Button } from "../ui/button";
import { startTransition } from "react";

export async function SidebarList() {
  const [chats, _] = useLocalStorage<Chat[]>("chats", []);
  return (
    <div className="flex flex-1 flex-col overflow-hidden">
      <div className="flex-1 overflow-auto">
        {chats?.length ? (
          <div className="space-y-2 px-2">
            <SidebarItems chats={chats} />
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
        <Button variant="ghost" size="icon" onClick={() => null}>
          <IconSettings />
        </Button>
      </div>
    </div>
  );
}
