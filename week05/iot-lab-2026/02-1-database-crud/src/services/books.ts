import { eq } from "drizzle-orm";
import { db } from "../db/index.js";
import { authors, books, type NewBook } from "../db/schema.js";

const bookSelection = {
  id: books.id,
  title: books.title,
  publishedYear: books.publishedYear,
  author: {
    id: authors.id,
    name: authors.name,
  },
};

export type BookInput = Omit<NewBook, "id">;
export type BookChanges = Partial<BookInput>;

export function getBooks() {
  return db
    .select(bookSelection)
    .from(books)
    .innerJoin(authors, eq(books.authorId, authors.id))
    .all();
}

export function getBookById(id: number) {
  return db
    .select(bookSelection)
    .from(books)
    .innerJoin(authors, eq(books.authorId, authors.id))
    .where(eq(books.id, id))
    .get();
}

export function createBook(input: BookInput) {
  const inserted = db
    .insert(books)
    .values(input)
    .returning({ id: books.id })
    .get();
  const book = getBookById(inserted.id);

  if (!book) {
    throw new Error("Created book could not be loaded");
  }

  return book;
}

export function updateBook(id: number, changes: BookChanges) {
  const updated = db
    .update(books)
    .set(changes)
    .where(eq(books.id, id))
    .returning({ id: books.id })
    .get();

  return updated ? getBookById(updated.id) : undefined;
}

export function deleteBook(id: number): boolean {
  return (
    db
      .delete(books)
      .where(eq(books.id, id))
      .returning({ id: books.id })
      .get() !== undefined
  );
}
