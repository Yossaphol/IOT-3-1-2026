import { z } from "zod";
import { positiveIdSchema } from "./common.js";

export const bookIdParamsSchema = z.strictObject({
  bookId: positiveIdSchema,
});

export const bookCreateSchema = z.strictObject({
  title: z.string().trim().min(1).max(200),
  publishedYear: z.number().int().nonnegative().nullable().optional(),
  authorId: z.number().int().positive().max(Number.MAX_SAFE_INTEGER),
});

export const bookUpdateSchema = bookCreateSchema.partial().refine(
  (book) => Object.keys(book).length > 0,
  { message: "At least one book field is required" },
);
