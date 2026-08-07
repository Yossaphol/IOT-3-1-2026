import { Hono } from "hono";
import { env } from "hono/adapter";
import { html } from "hono/html";
import { getBooks } from "../services/books.js";
import { Script } from "node:vm";

export const pagesController = new Hono();

pagesController.get("/", (c) => {
  const { NAME = "IT KMITL" } = env<{ NAME?: string }>(c);
  return c.json({ message: `Hello ${NAME}!` });
});

pagesController.get("/html", (c) => {
  const name = c.req.query("name") ?? "Hono Student";

  return c.html(
    html`<!doctype html>
      <html lang="en">
        <head>
          <meta charset="UTF-8" />
          <meta name="viewport" content="width=device-width, initial-scale=1" />
          <title>Hono HTML Example</title>
          <style>
            body {
              font-family: system-ui, sans-serif;
              max-width: 720px;
              margin: 3rem auto;
              padding: 0 1rem;
            }
            table {
              border-collapse: collapse;
              width: 100%;
            }
            th,
            td {
              border: 1px solid #ccc;
              padding: 0.5rem;
              text-align: left;
            }
          </style>
        </head>
        <body>
          <h1>Hello, ${name}!</h1>
          <p>The dynamic name is escaped automatically by Hono's HTML helper.</p>
          <table>
            <thead>
              <tr>
                <th>Title</th>
                <th>Author</th>
              </tr>
            </thead>
            <tbody>
              ${getBooks().map(
                (book) =>
                  html`<tr>
                    <td>${book.title}</td>
                    <td>${book.author}</td>
                  </tr>`,
              )}
            </tbody>
          </table>
          ${Script}
        </body>
      </html>`,
  );
});
