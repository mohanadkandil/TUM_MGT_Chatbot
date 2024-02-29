"use client";

import { Chat } from "@/lib/types";
import { AnimatePresence, motion } from "framer-motion";
import { SidebarItem } from "./sidebar-item";

interface SidebarItemsProps {
  chats: Chat[];
}

export function SidebarItems({ chats }: SidebarItemsProps) {
  if (!chats?.length) return null;

  return (
    <AnimatePresence>
      {chats.map((chat, idx) =>
        chat ? (
          <motion.div
            key={chat?.id}
            exit={{
              opacity: 0,
              height: 0,
            }}
          >
            <SidebarItem index={idx} chat={chat} />
          </motion.div>
        ) : null
      )}
    </AnimatePresence>
  );
}
