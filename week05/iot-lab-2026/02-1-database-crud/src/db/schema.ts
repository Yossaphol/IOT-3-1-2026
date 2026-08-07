import { index, integer, sqliteTable, text } from "drizzle-orm/sqlite-core";

export const authors = sqliteTable("authors", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  name: text("name").notNull(),
});

export const books = sqliteTable(
  "books",
  {
    id: integer("id").primaryKey({ autoIncrement: true }),
    title: text("title").notNull(),
    publishedYear: integer("published_year"),
    authorId: integer("author_id")
      .notNull()
      .references(() => authors.id, {
        onDelete: "restrict",
        onUpdate: "cascade",
      }),
  },
  (table) => [index("books_author_id_idx").on(table.authorId)],
);

export type Author = typeof authors.$inferSelect;
export type NewAuthor = typeof authors.$inferInsert;
export type Book = typeof books.$inferSelect;
export type NewBook = typeof books.$inferInsert;
