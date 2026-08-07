import { eq } from "drizzle-orm";
import { db } from "../db/index.js";
import { authors, books, type Author } from "../db/schema.js";

export interface AuthorWithBooks extends Author {
  books: Array<{
    id: number;
    title: string;
    publishedYear: number | null;
  }>;
}

export function getAuthors(): Author[] {
  return db.select().from(authors).all();
}

export function getAuthorById(id: number): AuthorWithBooks | undefined {
  const author = db.select().from(authors).where(eq(authors.id, id)).get();

  if (!author) {
    return undefined;
  }

  const authorBooks = db
    .select({
      id: books.id,
      title: books.title,
      publishedYear: books.publishedYear,
    })
    .from(books)
    .where(eq(books.authorId, id))
    .all();

  return { ...author, books: authorBooks };
}

export function authorExists(id: number): boolean {
  return db
    .select({ id: authors.id })
    .from(authors)
    .where(eq(authors.id, id))
    .get() !== undefined;
}

export function createAuthor(name: string): Author {
  return db.insert(authors).values({ name }).returning().get();
}

export function updateAuthor(id: number, name: string): Author | undefined {
  return db
    .update(authors)
    .set({ name })
    .where(eq(authors.id, id))
    .returning()
    .get();
}

export type DeleteAuthorResult = "deleted" | "not-found" | "has-books";

export function deleteAuthor(id: number): DeleteAuthorResult {
  return db.transaction((transaction) => {
    const author = transaction
      .select({ id: authors.id })
      .from(authors)
      .where(eq(authors.id, id))
      .get();

    if (!author) {
      return "not-found";
    }

    const relatedBook = transaction
      .select({ id: books.id })
      .from(books)
      .where(eq(books.authorId, id))
      .limit(1)
      .get();

    if (relatedBook) {
      return "has-books";
    }

    transaction.delete(authors).where(eq(authors.id, id)).run();
    return "deleted";
  });
}
