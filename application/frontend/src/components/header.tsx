"use client";
import React from "react";
import { ChatHistory } from "./sidebar/chat-history";
import { SidebarMobile } from "./sidebar/sidebar-mobile";
import { signIn, signOut, useSession } from "next-auth/react";

export function Header() {
  const { data: session } = useSession();

  return (
    <header className="z-50 w-full h-full lg:p-0 p-2">
      {session ? (
        <>
          <button onClick={() => signOut()}>Sign Out</button>
        </>
      ) : (
        <button onClick={() => signIn()}>Sign In</button> // Show sign-in
      )}
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
