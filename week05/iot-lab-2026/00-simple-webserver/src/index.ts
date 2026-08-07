import { serve } from "@hono/node-server";
import { app } from "./app.js";

serve({ fetch: app.fetch, port: 3000 }, ({ port }) =>
  console.log(`Server is running on http://localhost:${port}`),
);
