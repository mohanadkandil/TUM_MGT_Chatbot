import React from "react";
import { ChatHistory } from "./sidebar/chat-history";
import { SidebarMobile } from "./sidebar/sidebar-mobile";
export function Header() {
  return (
    <header className="z-50 w-full h-full lg:p-0 p-2">
      <div className="relative w-[230px] h-full">
        <React.Suspense fallback={<div className="flex-1 overflow-auto" />}>
          <SidebarMobile>
            <ChatHistory />
          </SidebarMobile>
        </React.Suspense>
      </div>
    </header>
  );
}
