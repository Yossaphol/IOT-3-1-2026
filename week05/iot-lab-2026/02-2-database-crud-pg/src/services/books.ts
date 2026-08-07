import { eq } from "drizzle-orm";
import db from "../db/index.js";
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

export async function getBooks() {
  return db
    .select(bookSelection)
    .from(books)
    .innerJoin(authors, eq(books.authorId, authors.id));
}

export async function getBookById(id: number) {
  const [book] = await db
    .select(bookSelection)
    .from(books)
    .innerJoin(authors, eq(books.authorId, authors.id))
    .where(eq(books.id, id))
    .limit(1);
  return book;
}

export async function createBook(input: BookInput) {
  const [inserted] = await db
    .insert(books)
    .values(input)
    .returning({ id: books.id });

  if (!inserted) {
    throw new Error("Created book was not returned");
  }

  const book = await getBookById(inserted.id);

  if (!book) {
    throw new Error("Created book could not be loaded");
  }

  return book;
}

export async function updateBook(id: number, changes: BookChanges) {
  const [updated] = await db
    .update(books)
    .set(changes)
    .where(eq(books.id, id))
    .returning({ id: books.id });

  return updated ? getBookById(updated.id) : undefined;
}

export async function deleteBook(id: number): Promise<boolean> {
  const [deleted] = await db
    .delete(books)
    .where(eq(books.id, id))
    .returning({ id: books.id });
  return deleted !== undefined;
}
