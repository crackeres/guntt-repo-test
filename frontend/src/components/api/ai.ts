const API_URL = import.meta.env.VITE_API_URL;

export const sendToAI = async (
  message: string,
  context: any
) => {

  console.log("📤 SEND TO BACKEND:", {
    message,
    context,
  });

  const response = await fetch(`${API_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      message,
      context,
    }),
  });

  console.log(
    "AI STATUS:",
    response.status
  );


  if (!response.ok) {

    const error = await response.text();

    console.error(
      "AI ERROR:",
      error
    );

    throw new Error(
      error || "Ошибка запроса к AI"
    );
  }

  const data = await response.json();

  console.log(
    "📥 AI RESPONSE FROM BACKEND:",
    data
  );

  return data;
};