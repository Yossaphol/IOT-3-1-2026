import { z } from "zod";
import { positiveIdSchema } from "./common.js";

export const authorIdParamsSchema = z.strictObject({
  authorId: positiveIdSchema,
});

export const authorBodySchema = z.strictObject({
  name: z.string().trim().min(1).max(100),
});
