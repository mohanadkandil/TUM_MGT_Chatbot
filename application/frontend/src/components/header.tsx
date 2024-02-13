import React from "react";
import { buttonVariants } from "./ui/button";
import { cn } from "@/lib/utils";

export function Header() {
  return (
    <header className="sticky top-0 z-50 flex items-center justify-between w-full h-16 px-4 border-b shrink-0 bg-gradient-to-b from-background/10 via-background/50 to-background/80 backdrop-blur-xl">
      <div className="flex items-center">
        <React.Suspense
          fallback={<div className="flex-1 overflow-auto" />}
        ></React.Suspense>
      </div>
      <div className="flex items-center justify-end space-x-2">
        <a
          target="_blank"
          href=""
          rel="noopener noreferrer"
          className={cn(buttonVariants({ variant: "outline" }))}
        >
          <span className="hidden ml-2 md:flex">Home</span>
        </a>
        <a href="/" target="_blank" className={cn(buttonVariants())}>
          <span className="hidden sm:block">Contact</span>
          <span className="sm:hidden">Contact</span>
        </a>
      </div>
    </header>
  );
}
