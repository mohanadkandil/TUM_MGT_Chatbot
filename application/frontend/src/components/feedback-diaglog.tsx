"use client";

import { Button } from "./ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "./ui/label";
import { useState } from "react";

interface FeedbackDialogueOption {
  id: string;
  label: string;
}

export interface FeedbackDialogue {
  id: string;
  buttonTitle: string;
  description: string;
  options: FeedbackDialogueOption[];
}

function FeedbackDialog({
  dialogue,
  onUpdate,
}: {
  dialogue: FeedbackDialogue;
  onUpdate: (optionId: string, isSelected: boolean) => void;
}) {
  const [selectedOptions, setSelectedOptions] = useState<{
    [key: string]: boolean;
  }>({});

  const toggleOption = (optionId: string) => {
    const newState = !selectedOptions[optionId];
    setSelectedOptions({ ...selectedOptions, [optionId]: newState });
    onUpdate(optionId, newState);
  };

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm">
          {dialogue.buttonTitle}
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>{dialogue.description}</DialogTitle>
          <DialogDescription>Select all that apply. </DialogDescription>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="flex flex-col items-start w-fit gap-4">
            {dialogue.options.map((option) => (
              <Button
                key={option.id}
                variant={selectedOptions[option.id] ? "secondary" : "outline"}
                size="sm"
                onClick={() => toggleOption(option.id)}
              >
                {option.label}
              </Button>
            ))}
          </div>

          <div className="grid grid-cols-2 items-center gap-2">
            <Label htmlFor="username" className="text-left">
              How can the response be improved? (optional)
            </Label>
            <Input
              id="username"
              placeholder="Your feedback..."
              className="col-span-3"
            />
          </div>
        </div>
        <DialogFooter>
          <Button type="submit">Submit</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

export default FeedbackDialog;
