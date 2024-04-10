import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { useDisclaimerChoice } from "@/lib/stores/useDisclaimerChoice";
import ReactMarkdown from "react-markdown";

const disclaimerMarkdown = `
Dear User, 

Thank you for your interest in our TUM MGT Chatbot! With this research project, we aim to explore whether generative AI can support human administration in the education sector.
### Capabilities, Limitations, and Restrictions
- **Feedback:** Your feedback is crucial for enhancing the performance of the TUM MGT Chatbot. By evaluating specific responses or entire conversations, you contribute to the gradual improvement of its functionality.
- **Contextual Understanding:** The TUM MGT Chatbot utilizes documents provided by the TUM School of Management to answer questions, thereby assisting you with inquiries.
- **Misinformation:** Language models are subject to certain risks concerning hallucinations or the fabrication of facts. We have undertaken the best possible measures to prevent this. Please be aware during your interaction that the chatbot's responses do not carry legal validity.
### Data Processing & Consent
- **Data Processing:** Your interactions with the TUM MGT Chatbot are processed by Microsoft and OpenAI via Microsoft Azure OpenAI. This means that the information you share with the TUM MGT Chatbot is sent to our Azure Cloud. Your chats are not used for OpenAI's training purposes and are deleted after 30 days. Furthermore, your chats are stored locally in your browser for review.
- **Consent:** To use the TUM MGT Chatbot, you must accept the consent form. By doing so, you agree to the processing of your data by Microsoft Azure OpenAI as described. By clicking the "Agree" button, you confirm your agreement with the consent form and the privacy policy.
`;

export function DisclaimerDialog() {
  const setDialogAccepted = useDisclaimerChoice((state) => state.setAccepted);

  const handleAccept = () => setDialogAccepted(true);
  const handleDecline = () => setDialogAccepted(false);

  return (
    <Dialog>
      <DialogTrigger asChild>
        <button className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
          Accept terms and conditions
        </button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle>Welcome to the TUM MGT Chabot!</DialogTitle>
          <DialogDescription>
            This project aims to explore how generative AI can help us at TUM.
          </DialogDescription>
        </DialogHeader>
        <div className="max-h-[300px] overflow-y-scroll p-4 bg-card">
          <ReactMarkdown className="whitespace-pre-wrap	">
            {disclaimerMarkdown}
          </ReactMarkdown>
        </div>
        <DialogFooter>
          <DialogClose asChild>
            <Button onClick={handleDecline}>Decline</Button>
          </DialogClose>
          <DialogClose asChild>
            <Button onClick={handleAccept}>Accept</Button>
          </DialogClose>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
