import FeedbackDialog, { FeedbackDialogue } from "./feedback-diaglog";
import { Card, CardContent } from "./ui/card";

// Define a type for the feedback Dialogues
const feedbackDialogues: FeedbackDialogue[] = [
  {
    id: "resolved",
    description: "Great! What did you like the most?",
    buttonTitle: "👏 Fully Resolved!",
    options: [
      { id: "clarity", label: "The clarity of the information provided" },
      { id: "coverage", label: "The comprehensive coverage of topics" },
      { id: "speed", label: "The speed of the response" },
    ],
  },
  {
    id: "improvement",
    description: "How can we improve?",
    buttonTitle: "🤔 Okay, but could be better",
    options: [
      { id: "responseTime", label: "Faster response times" },
      { id: "accuracy", label: "More accurate information" },
      { id: "instructions", label: "Clearer instructions" },
    ],
  },
  {
    id: "disappointment",
    description: "Sorry. Please help us understand the issues.",
    buttonTitle: "🤔 Okay, but could be better",
    options: [
      { id: "understanding", label: "My issue was not understood" },
      { id: "notResolved", label: "My issue was not resolved" },
      { id: "responseTime", label: "The response took too long" },
      { id: "unclear", label: "The instructions were unclear" },
      {
        id: "technicalProblems",
        label: "I had technical problems with the service",
      },
    ],
  },
];

export function ChatFeedback() {
  const handleUpdate = (selectedLabels: string[], feedbackText: string) => {
    // Implement your logic for handling option selection
  };

  return (
    <div className="sm:pb-8 pb-16">
      <Card className="mx-auto">
        <CardContent className="flex flex-row flex-wrap items-center justify-center h-full py-4">
          <span className="text-sm font-medium text-center whitespace-nowrap mr-2">
            Did we resolve your issue today?
          </span>
          <div className="flex items-center gap-2 justify-center">
            {feedbackDialogues.map((dialogue) => (
              <FeedbackDialog
                key={dialogue.id}
                dialogue={dialogue}
                onUpdate={handleUpdate}
              />
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
