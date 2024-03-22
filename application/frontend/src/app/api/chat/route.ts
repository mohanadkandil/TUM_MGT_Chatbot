
interface RequestBody {
  data: string; 
}
export async function POST(req: Request) {
  const body = await req.json()
  const { data } = body
  const encodedQuestion = encodeURIComponent(data);
  const url = `https://copilot-tum-mgt.de/conversation?question=${encodedQuestion}`;

  try {
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
            content: data,
          },
        ],
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return new Response(response.body)
    // Handle success response here, such as updating UI or state accordingly
  } catch (error) {
    return new Response(
      'Could not post to input at this time. Please try later',
      { status: 500 }
    )
  }
}