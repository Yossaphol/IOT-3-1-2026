import { zValidator } from "@hono/zod-validator";
import { Hono } from "hono";
import {
  bookCreateSchema,
  bookIdParamsSchema,
  bookUpdateSchema,
} from "../schemas/books.js";
import { authorExists } from "../services/authors.js";
import {
  createBook,
  deleteBook,
  getBookById,
  getBooks,
  updateBook,
} from "../services/books.js";

export const booksController = new Hono();

booksController.get("/", (c) => c.json(getBooks()));

booksController.get(
  "/:bookId",
  zValidator("param", bookIdParamsSchema),
  (c) => {
    const { bookId } = c.req.valid("param");
    const book = getBookById(bookId);

    if (!book) {
      return c.json({ error: "Book not found" }, 404);
    }

    return c.json(book);
  },
);

booksController.post(
  "/",
  zValidator("json", bookCreateSchema),
  (c) => {
    const input = c.req.valid("json");

    if (!authorExists(input.authorId)) {
      return c.json({ error: "authorId does not reference an author" }, 422);
    }

    const book = createBook(input);
    c.header("Location", `/api/books/${book.id}`);
    return c.json(book, 201);
  },
);

booksController.patch(
  "/:bookId",
  zValidator("param", bookIdParamsSchema),
  zValidator("json", bookUpdateSchema),
  (c) => {
    const { bookId } = c.req.valid("param");
    const changes = c.req.valid("json");

    if (
      changes.authorId !== undefined &&
      !authorExists(changes.authorId)
    ) {
      return c.json({ error: "authorId does not reference an author" }, 422);
    }

    const book = updateBook(bookId, changes);

    if (!book) {
      return c.json({ error: "Book not found" }, 404);
    }

    return c.json(book);
  },
);

booksController.delete(
  "/:bookId",
  zValidator("param", bookIdParamsSchema),
  (c) => {
    const { bookId } = c.req.valid("param");

    if (!deleteBook(bookId)) {
      return c.json({ error: "Book not found" }, 404);
    }

    return c.body(null, 204);
  },
);
