import { date, integer, pgTable, text } from "drizzle-orm/pg-core";

export const students = pgTable("students", {
  id: integer("id").primaryKey().generatedAlwaysAsIdentity(),
  firstname: text("firstname").notNull(),
  lastname: text("lastname").notNull(),
  studentID: integer("studentid").notNull(),
  birth: date("birth").notNull(),
  sex: text("sex").notNull(),
});

export type Student = typeof students.$inferSelect;
export type NewStudent = typeof students.$inferInsert;