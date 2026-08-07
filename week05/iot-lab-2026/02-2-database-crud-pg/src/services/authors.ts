import { and, eq, notExists } from "drizzle-orm";
import db from "../db/index.js";
import { authors, books, type Author } from "../db/schema.js";

export interface AuthorWithBooks extends Author {
  books: Array<{
    id: number;
    title: string;
    publishedYear: number | null;
  }>;
}

export async function getAuthors(): Promise<Author[]> {
  return db.select().from(authors);
}

export async function getAuthorById(
  id: number,
): Promise<AuthorWithBooks | undefined> {
  const [author] = await db
    .select()
    .from(authors)
    .where(eq(authors.id, id))
    .limit(1);

  if (!author) {
    return undefined;
  }

  const authorBooks = await db
    .select({
      id: books.id,
      title: books.title,
      publishedYear: books.publishedYear,
    })
    .from(books)
    .where(eq(books.authorId, id));

  return { ...author, books: authorBooks };
}

export async function authorExists(id: number): Promise<boolean> {
  const [author] = await db
    .select({ id: authors.id })
    .from(authors)
    .where(eq(authors.id, id))
    .limit(1);
  return author !== undefined;
}

export async function createAuthor(name: string): Promise<Author> {
  const [author] = await db.insert(authors).values({ name }).returning();

  if (!author) {
    throw new Error("Created author was not returned");
  }

  return author;
}

export async function updateAuthor(
  id: number,
  name: string,
): Promise<Author | undefined> {
  const [author] = await db
    .update(authors)
    .set({ name })
    .where(eq(authors.id, id))
    .returning();
  return author;
}

export type DeleteAuthorResult = "deleted" | "not-found" | "has-books";

export async function deleteAuthor(id: number): Promise<DeleteAuthorResult> {
  const [deleted] = await db
    .delete(authors)
    .where(
      and(
        eq(authors.id, id),
        notExists(
          db
            .select({ id: books.id })
            .from(books)
            .where(eq(books.authorId, authors.id)),
        ),
      ),
    )
    .returning({ id: authors.id });

  if (deleted) {
    return "deleted";
  }

  return (await authorExists(id)) ? "has-books" : "not-found";
}
