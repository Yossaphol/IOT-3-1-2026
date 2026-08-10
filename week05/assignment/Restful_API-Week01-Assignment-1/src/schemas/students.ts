import { z } from "zod";
import { positiveIdSchema } from "./common.js";

export const studentIdParamsSchema = z.strictObject({
  studentId: positiveIdSchema,
});

export const studentBodySchema = z.strictObject({
  firstname: z.string().trim().min(1).max(100),
  lastname: z.string().trim().min(1).max(100),
  studentID: z.number().int().positive(),
  birth: z.string().regex(
    /^\d{4}-\d{2}-\d{2}$/,
    "Invalid date format"
  ),
  sex: z.string().trim().min(1).max(20)
});

export const studentPatchSchema = studentBodySchema.partial();