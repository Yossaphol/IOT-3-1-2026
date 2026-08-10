import { zValidator } from "@hono/zod-validator";
import { Hono } from "hono";
import { studentBodySchema, studentIdParamsSchema, studentPatchSchema } from "../schemas/students.js";
import {
  createStudent,
  deleteStudent,
  getStudentById,
  getStudents,
  updateStudent,
  updateStudentPartial
} from "../services/students.js";

export const studentsController = new Hono();

studentsController.get("/", async (c) => c.json(await getStudents()));

studentsController.get("/:studentId", zValidator("param", studentIdParamsSchema), async (c) => {
  const { studentId } = c.req.valid("param");
  const student = await getStudentById(studentId);

  if (!student) {
    return c.json({ error: "Student not found" }, 404);
  }

  return c.json(student);
});

studentsController.post("/", zValidator("json", studentBodySchema), async (c) => {
  const { firstname } = c.req.valid("json");
  const { lastname } = c.req.valid("json");
  const { studentID } = c.req.valid("json");
  const { birth } = c.req.valid("json");
  const { sex } = c.req.valid("json");
  const student = await createStudent(firstname, lastname, studentID, birth, sex);
  c.header("Location", `/api/students/${student.id}`);
  return c.json(student, 201);
});

studentsController.put(
  "/:studentId",
  zValidator("param", studentIdParamsSchema),
  zValidator("json", studentBodySchema),
  async (c) => {
    const { studentId } = c.req.valid("param");
    const { firstname } = c.req.valid("json");
    const { lastname } = c.req.valid("json");
    const { studentID } = c.req.valid("json");
    const { birth } = c.req.valid("json");
    const { sex } = c.req.valid("json");
    const student = await updateStudent(studentId, firstname, lastname, studentID, birth, sex);

    if (!student) {
      return c.json({ error: "Student not found" }, 404);
    }

    return c.json(student);
  },
);

studentsController.patch(
  "/:studentId",
  zValidator("param", studentIdParamsSchema),
  zValidator("json", studentPatchSchema),
  async (c) => {
    const { studentId } = c.req.valid("param");
    const data = c.req.valid("json");

    const student = await updateStudentPartial(studentId, data);

    if (!student) {
      return c.json({ error: "Student not found" }, 404);
    }

    return c.json(student);
  },
);

studentsController.delete("/:studentId", zValidator("param", studentIdParamsSchema), async (c) => {
  const { studentId } = c.req.valid("param");
  const result = await deleteStudent(studentId);

  if (result === "not-found") {
    return c.json({ error: "Student not found" }, 404);
  }

  return c.body(null, 204);
});