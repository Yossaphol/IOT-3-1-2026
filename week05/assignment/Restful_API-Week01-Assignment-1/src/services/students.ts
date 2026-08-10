import { and, eq, notExists } from "drizzle-orm";
import db from "../db/index.js";
import { students, type Student } from "../db/schema.js";

export async function getStudents(): Promise<Student[]> {
  return db.select().from(students);
}

export async function getStudentById(
  id: number,
): Promise<Student | undefined> {
  const [student] = await db
    .select()
    .from(students)
    .where(eq(students.id, id))
    .limit(1);

  return student;
}

export async function studentExists(id: number): Promise<boolean> {
  const [student] = await db
    .select({ id: students.id })
    .from(students)
    .where(eq(students.id, id))
    .limit(1);

  return student !== undefined;
}

export async function createStudent(
  firstname: string,
  lastname: string,
  studentID: number,
  birth: string,
  sex: string,
): Promise<Student> {
  const [student] = await db.insert(students).values({ firstname, lastname, studentID, birth, sex }).returning();

  if (!student) {
    throw new Error("Created student was not returned");
  }

  return student;
}

export async function updateStudent(
  id: number,
  firstname: string,
  lastname: string,
  studentID: number,
  birth: string,
  sex: string,
): Promise<Student | undefined> {
  const [student] = await db
    .update(students)
    .set({firstname, lastname, studentID, birth, sex,})
    .where(eq(students.id, id))
    .returning();

  return student;
}

export async function updateStudentPartial(
  id: number,
  data: Partial<{
    firstname: string;
    lastname: string;
    studentID: number;
    birth: string;
    sex: string;
  }>,
): Promise<Student | undefined> {
  const [student] = await db
    .update(students)
    .set(data)
    .where(eq(students.id, id))
    .returning();

  return student;
}

export type DeleteStudentResult = "deleted" | "not-found";

export async function deleteStudent(
  id: number,
): Promise<DeleteStudentResult> {
  const [deleted] = await db
    .delete(students)
    .where(eq(students.id, id))
    .returning({ id: students.id });

  if (deleted) {
    return "deleted";
  }

  return "not-found";
}