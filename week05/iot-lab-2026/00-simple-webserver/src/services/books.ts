export interface Book {
  id: number;
  title: string;
  author: string;
}

const books: readonly Book[] = [
  { id: 1, title: "1984", author: "George Orwell" },
  { id: 2, title: "The Little Prince", author: "Antoine de Saint-Exupéry" },
  { id: 3, title: "The Hobbit", author: "J.R.R. Tolkien" },
];

export function getBooks(): readonly Book[] {
  return books;
}

export function getBookById(id: number): Book | undefined {
  return books.find((book) => book.id === id);
}
