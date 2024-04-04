import axios from "axios";

export async function POST(req: Request) {
  const body = await req.json()
  const { feedback_classification, feedback_text  } = body
  const url = "https://copilot-tum-mgt.de/feedback";

  try {
    const response = await axios.post(url, {
      uuid: "string", // Consider generating or retrieving a meaningful UUID
      feedback_classification,
      feedback_text,
    });

    return new Response(response.data)
    // Handle success response here, such as updating UI or state accordingly
  } catch (error) {
    return new Response(
      `${error}`,
      { status: 500 }
    )
  }
}