import React from "react";
import { ChatHistory } from "./sidebar/chat-history";
import { SidebarMobile } from "./sidebar/sidebar-mobile";
import { SidebarToggle } from "./sidebar/sidebar-toggle";
export function Header() {
  return (
    <header className="sticky top-0 z-50 flex items-center justify-between w-full h-12 px-4 shrink-0">
      <div className="flex items-center">
        <React.Suspense fallback={<div className="flex-1 overflow-auto" />}>
          <SidebarMobile>
            <ChatHistory />
          </SidebarMobile>
          <SidebarToggle />
        </React.Suspense>
      </div>
    </header>
  );
}
