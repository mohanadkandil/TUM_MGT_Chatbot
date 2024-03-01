"use client";

import { useTheme } from "next-themes";
import * as React from "react";
import { Button } from "../ui/button";
import { IconMoon, IconSun } from "../icons";
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
