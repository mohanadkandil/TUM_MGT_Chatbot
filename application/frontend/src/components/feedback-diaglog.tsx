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
  DialogClose,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "./ui/label";
import { useState } from "react";
import { useFeedbackTrigger } from "@/app/api/api";

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
  onUpdate: (selectedLabels: string[], feedbackText: string) => void;
}) {
  const [selectedOptions, setSelectedOptions] = useState<{
    [key: string]: boolean;
  }>({});
  const [feedbackText, setFeedbackText] = useState("");

  const toggleOption = (optionId: string) => {
    const newState = !selectedOptions[optionId];
    setSelectedOptions({ ...selectedOptions, [optionId]: newState });
  };

  const isSubmitDisabled =
    Object.values(selectedOptions).every((v) => !v) && !feedbackText.trim();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (isSubmitDisabled) return;

    const selectedLabels = dialogue.options
      .filter((option) => selectedOptions[option.id])
      .map((option) => option.label);

    if (selectedLabels.length === 0 && !feedbackText.trim()) {
      console.log("No options selected or feedback provided");
      return;
    }

    onUpdate(selectedLabels, feedbackText);

    triggerFeedback({
      uuid: "",
      feedback_classification: selectedLabels.toString(),
      feedback_text: feedbackText,
    });

    // Reset state if needed
    setSelectedOptions({});
    setFeedbackText("");
  };

  const { triggerFeedback, isSuccess, isPending } = useFeedbackTrigger();

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
              id="feedbackText"
              placeholder="Your feedback..."
              className="col-span-3"
              onChange={(e) => setFeedbackText(e.target.value)}
            />
          </div>
        </div>
        <form onSubmit={handleSubmit}>
          <DialogFooter>
            <DialogClose asChild>
              <Button type="submit" disabled={isSubmitDisabled}>
                Submit
              </Button>
            </DialogClose>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

export default FeedbackDialog;
