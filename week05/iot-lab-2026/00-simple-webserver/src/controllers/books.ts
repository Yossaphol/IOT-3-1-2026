import { Hono } from "hono";
import { bearerAuth } from "hono/bearer-auth";
import { getBookById, getBooks } from "../services/books.js";

const apiToken = process.env.SECRET_PASSWORD;

if (!apiToken) {
  throw new Error("SECRET_PASSWORD is required");
}

export const booksController = new Hono();

booksController.use("*", bearerAuth({ token: apiToken }));

booksController.get("/", (c) => c.json(getBooks()));

booksController.get("/:bookId", (c) => {
  const rawBookId = c.req.param("bookId");

  if (!/^[1-9]\d*$/.test(rawBookId)) {
    return c.json({ error: "bookId must be a positive integer" }, 400);
  }

  const bookId = Number(rawBookId);

  if (!Number.isSafeInteger(bookId)) {
    return c.json({ error: "bookId is too large" }, 400);
  }

  const book = getBookById(bookId);

  if (!book) {
    return c.json({ error: "Book not found" }, 404);
  }

  return c.json(book);
});
