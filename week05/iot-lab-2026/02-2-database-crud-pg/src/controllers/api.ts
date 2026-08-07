import { Hono } from "hono";
import { bearerAuth } from "hono/bearer-auth";
import { authorsController } from "./authors.js";
import { booksController } from "./books.js";

const apiToken = process.env.SECRET_PASSWORD;

if (!apiToken) {
  throw new Error("SECRET_PASSWORD is required");
}

export const apiController = new Hono();

apiController.use("*", bearerAuth({ token: apiToken }));
apiController.route("/authors", authorsController);
apiController.route("/books", booksController);
