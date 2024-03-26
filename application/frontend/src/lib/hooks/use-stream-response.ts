import { useState } from "react"
import { useMutation } from "@tanstack/react-query"

export function useStreamResponse({
  streamCallback,
}: {
  streamCallback: React.Dispatch<React.SetStateAction<string>>
}) {
  const [isLoading, setIsLoading] = useState(false)
  const [isTriggerFeedback, setIsTriggerFeedback] = useState(false)
  const [responses, setResponses] = useState("")
  const [streamingFinished, setStreamingFinished] = useState(false);
  const [finalAnswer, setFinalAnswer] = useState("")
  const { mutate: startStream, isError } = useMutation({
    mutationFn: async (message: string) => {
      const encodedQuestion = encodeURIComponent(message);
      const url = `${process.env.ROOTURL}/chat_stream/?question=${encodedQuestion}`;
      const response = await fetch(url, {
        method: "POST",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          conversation: [
            {
              role: "string", 
              content: message,
            },
          ],
          "uuid": "string",
          "study_program": "string"
        }),
      })

      if (!response.body) {
        throw new Error("ReadableStream not supported in this browser.")
      }
      
      const reader = response.body.getReader()
      return reader
    },
    onSuccess: (reader) => {
      setIsLoading(true)
      readStream(reader)
    },
  })

  async function readStream(reader: ReadableStreamDefaultReader) {
    let accumulatedText = ''; // Buffer to accumulate streamed text
  
    async function read() {
      const { done, value } = await reader.read();
      if (done) {
        // Process any remaining accumulated text before finishing
        if (accumulatedText) {
          processTextChunk(accumulatedText);
        }
        setStreamingFinished(true); // Signal that streaming is finished
        setIsLoading(false)
        return;
      }
  
      const textChunk = new TextDecoder().decode(value);
      accumulatedText += textChunk;
  
      // Split the accumulated text by new lines, which indicates potential end of JSON objects
      let splitIndex;
      while ((splitIndex = accumulatedText.indexOf("\ndata: ")) >= 0) {
        const completeChunk = accumulatedText.substring(0, splitIndex);
        processTextChunk(completeChunk);
        accumulatedText = accumulatedText.substring(splitIndex + 1);
      }
      read();
    }
  
    function processTextChunk(chunk: string) {
      if (chunk.startsWith("data: ")) {
        const jsonPart = chunk.substring("data: ".length);
        try {
          const obj = JSON.parse(jsonPart);
          if (obj && obj.type === "stream" && obj.data) {
            const streamData = obj.data;            
            setResponses((prev) => prev + streamData);
            streamCallback(streamData);
          } else if (obj && obj.type === "final" && obj.data && obj.data.       full_answer) {
            // If the data type is "final", handle the full_answer specifically
            const finalAnswer = obj.data.full_answer;
            setIsTriggerFeedback(obj.data.feedback_trigger)
            // Assuming you want to use setResponses to store the final answer
            streamCallback(finalAnswer)
            setStreamingFinished(false)
            setResponses(finalAnswer)
            setFinalAnswer(finalAnswer); // Update this line if you need a different behavior
            // Optionally, if you have a separate callback or state for the final answer, use it here
            // For example: finalCallback(finalAnswer);
          }
        } catch (e) {
          console.error("Failed to parse JSON chunk:", e);
        }
      }
    }
  
    read().catch(e => console.error("Stream reading failed:", e));
  }

  return { responses, startStream, isError, isLoading, isTriggerFeedback, streamingFinished, finalAnswer };
}