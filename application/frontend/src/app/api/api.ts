import { toast } from "@/components/ui/use-toast";
import { useMutation } from "@tanstack/react-query";
import axios, { AxiosError } from "axios";

interface FeedbackMutationParams {
  feedback_classification: string; // Adjust the type as necessary
  feedback_text: string;
  uuid: string
}

export function useFeedbackTrigger() {
  const { mutate: triggerFeedback, isSuccess, isPending } = useMutation<void, AxiosError, FeedbackMutationParams>({
    mutationFn: async ({ feedback_classification, feedback_text, uuid }) => {
      return axios.post('/api/feedback', { feedback_classification, feedback_text, uuid });
    },
    onSuccess: () => {
      toast({
        variant: "default",
        title: "Feedback Submitted",
        description: "Thank you for your feedback!",
      });
    },
    onError: () => {
      toast({
        variant: "destructive",
        title: "Submission Failed",
        description: "Please try submitting your feedback again later.",
      });
    },
  });  

  return { triggerFeedback, isSuccess, isPending };
}