import { serveStatic } from "@hono/node-server/serve-static";
import { Hono } from "hono";
import { booksController } from "./controllers/books.js";
import { pagesController } from "./controllers/pages.js";

export const app = new Hono();

app.route("/", pagesController);
app.route("/api/books", booksController);
app.use("*", serveStatic({ root: "./public" }));
