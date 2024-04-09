import * as React from "react";

import Link from "next/link";

import { cn } from "@/lib/utils";
import { SidebarList } from "./sidebar-list";
import { buttonVariants } from "../ui/button";
import { IconPencil, IconTUMLogo } from "../icons";
import { SidebarToggle } from "./sidebar-toggle";

export async function ChatHistory() {
  return (
    <div className="flex flex-col h-full px-3 bg-card">
      <div className="my-4 px-3">
        <IconTUMLogo />
        <Link
          href="/chat"
          className={cn(
            buttonVariants({ variant: "outline" }),
            "rounded-full h-10 justify-start px-4 mt-9 mb-6 shadow-none transition-colors bg-button-gradient"
          )}
        >
          <IconPencil className="-translate-x-1 stroke-2 text-[4px] text-white" />
          <span className="text-white">New Chat</span>
        </Link>
      </div>
      <React.Suspense
        fallback={
          <div className="flex flex-col flex-1 px-4 space-y-4 overflow-auto">
            {Array.from({ length: 10 }).map((_, idx) => (
              <div
                key={idx}
                className="w-full h-6 rounded-md shrink-0 animate-pulse bg-zinc-200 dark:bg-zinc-800"
              />
            ))}
          </div>
        }
      >
        <SidebarList />
        <SidebarToggle />
      </React.Suspense>
    </div>
  );
}
