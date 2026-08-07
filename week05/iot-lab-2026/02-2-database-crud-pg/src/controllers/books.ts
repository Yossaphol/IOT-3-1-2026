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

booksController.get("/", async (c) => c.json(await getBooks()));

booksController.get(
  "/:bookId",
  zValidator("param", bookIdParamsSchema),
  async (c) => {
    const { bookId } = c.req.valid("param");
    const book = await getBookById(bookId);

    if (!book) {
      return c.json({ error: "Book not found" }, 404);
    }

    return c.json(book);
  },
);

booksController.post(
  "/",
  zValidator("json", bookCreateSchema),
  async (c) => {
    const input = c.req.valid("json");

    if (!(await authorExists(input.authorId))) {
      return c.json({ error: "authorId does not reference an author" }, 422);
    }

    const book = await createBook(input);
    c.header("Location", `/api/books/${book.id}`);
    return c.json(book, 201);
  },
);

booksController.patch(
  "/:bookId",
  zValidator("param", bookIdParamsSchema),
  zValidator("json", bookUpdateSchema),
  async (c) => {
    const { bookId } = c.req.valid("param");
    const changes = c.req.valid("json");

    if (
      changes.authorId !== undefined &&
      !(await authorExists(changes.authorId))
    ) {
      return c.json({ error: "authorId does not reference an author" }, 422);
    }

    const book = await updateBook(bookId, changes);

    if (!book) {
      return c.json({ error: "Book not found" }, 404);
    }

    return c.json(book);
  },
);

booksController.delete(
  "/:bookId",
  zValidator("param", bookIdParamsSchema),
  async (c) => {
    const { bookId } = c.req.valid("param");

    if (!(await deleteBook(bookId))) {
      return c.json({ error: "Book not found" }, 404);
    }

    return c.body(null, 204);
  },
);
