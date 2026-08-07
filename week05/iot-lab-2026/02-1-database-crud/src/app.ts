import { Hono } from "hono";
import { HTTPException } from "hono/http-exception";
import { apiController } from "./controllers/api.js";

export const app = new Hono();

app.route("/api", apiController);

app.notFound((c) => c.json({ error: "Route not found" }, 404));

app.onError((error, c) => {
  if (error instanceof HTTPException) {
    const response = error.getResponse();
    const headers = new Headers(response.headers);
    headers.set("Content-Type", "application/json; charset=UTF-8");

    return new Response(
      JSON.stringify({
        error: error.status === 401 ? "Unauthorized" : "Request failed",
      }),
      { status: response.status, headers },
    );
  }

  console.error(error);
  return c.json({ error: "Internal server error" }, 500);
});
