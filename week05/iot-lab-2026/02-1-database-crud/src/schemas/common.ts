import { z } from "zod";

export const positiveIdSchema = z
  .string()
  .regex(/^[1-9]\d*$/, "must be a positive integer")
  .transform(Number)
  .pipe(z.number().int().positive().max(Number.MAX_SAFE_INTEGER));
