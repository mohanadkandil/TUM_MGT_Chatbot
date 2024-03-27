"use client";

import * as React from "react";

import { useSidebar } from "@/lib/hooks/use-sidebar";
import { Button } from "@/components/ui/button";
import { IconThreeDots } from "../icons";

export function SidebarToggle() {
  const { toggleSidebar } = useSidebar();

  return (
    <Button
      variant="link"
      className="ml-2 size-6 p-0 absolute left-[100%] top-1/2 dark:text-slate-400 dark:hover:text-white"
      onClick={() => {
        toggleSidebar();
      }}
    >
      <IconThreeDots className="size-6 " />
      <span className="sr-only">Toggle Sidebar</span>
    </Button>
  );
}
