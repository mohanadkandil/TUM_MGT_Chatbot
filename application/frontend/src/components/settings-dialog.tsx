import { Label } from "@radix-ui/react-label";
import { Button } from "./ui/button";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "./ui/dialog";
import { Input } from "./ui/input";
import { IconSettings } from "./icons";
import { SettingsTabs } from "./settings-tabs";

export function SettingsDialog() {
  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="ghost" size="icon">
          <IconSettings />
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[600px] sm-h-[500px] h-[600px]">
        <DialogHeader>
          <DialogTitle className="border-b py-4">Settings</DialogTitle>
        </DialogHeader>
        <SettingsTabs />
      </DialogContent>
    </Dialog>
  );
}
