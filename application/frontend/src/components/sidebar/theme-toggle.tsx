"use client";

import * as React from "react";
import { useTheme } from "next-themes";
import { Switch } from "../ui/switch";

export function ThemeToggle() {
  const { setTheme, theme } = useTheme();
  const [_, startTransition] = React.useTransition();

  return (
    <Switch
      onClick={() => {
        startTransition(() => {
          setTheme(theme === "light" ? "dark" : "light");
        });
      }}
    />
  );
}
