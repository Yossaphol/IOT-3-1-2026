import { zValidator } from "@hono/zod-validator";
import { Hono } from "hono";
import { authorBodySchema, authorIdParamsSchema } from "../schemas/authors.js";
import {
  createAuthor,
  deleteAuthor,
  getAuthorById,
  getAuthors,
  updateAuthor,
} from "../services/authors.js";

export const authorsController = new Hono();

authorsController.get("/", (c) => c.json(getAuthors()));

authorsController.get("/:authorId", zValidator("param", authorIdParamsSchema), (c) => {
  const { authorId } = c.req.valid("param");
  const author = getAuthorById(authorId);

  if (!author) {
    return c.json({ error: "Author not found" }, 404);
  }

  return c.json(author);
});

authorsController.post("/", zValidator("json", authorBodySchema), (c) => {
  const { name } = c.req.valid("json");
  const author = createAuthor(name);
  c.header("Location", `/api/authors/${author.id}`);
  return c.json(author, 201);
});

authorsController.patch(
  "/:authorId",
  zValidator("param", authorIdParamsSchema),
  zValidator("json", authorBodySchema),
  (c) => {
    const { authorId } = c.req.valid("param");
    const { name } = c.req.valid("json");
    const author = updateAuthor(authorId, name);

    if (!author) {
      return c.json({ error: "Author not found" }, 404);
    }

    return c.json(author);
  },
);

authorsController.delete("/:authorId", zValidator("param", authorIdParamsSchema), (c) => {
  const { authorId } = c.req.valid("param");
  const result = deleteAuthor(authorId);

  if (result === "not-found") {
    return c.json({ error: "Author not found" }, 404);
  }

  if (result === "has-books") {
    return c.json({ error: "Delete the author's books before deleting the author" }, 409);
  }

  return c.body(null, 204);
});
