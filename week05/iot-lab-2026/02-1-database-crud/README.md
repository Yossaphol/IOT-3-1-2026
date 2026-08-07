# SQLite CRUD API with Hono and Drizzle

A student template for a REST API with SQLite, Drizzle ORM, bearer authentication, Zod v4 validation, and related resources.

## Data model

```text
authors (1) ─────< books (many)

books.author_id → authors.id
```

Every book must reference an existing author. An author cannot be deleted while books still reference it.

## Setup

```sh
nvm install 24.14.1
nvm use 24.14.1
npm install
copy .env.example .env
npm run db:migrate
npm run dev
```

On macOS or Linux, use `cp .env.example .env` instead of `copy`.

The API runs at <http://localhost:3000/api>. All routes require:

```text
Authorization: Bearer iot-lab-2026
Content-Type: application/json
```

Do not commit `.env` or SQLite database files.

## Routes

### Authors

| Method | Route | Result |
| --- | --- | --- |
| `GET` | `/api/authors` | List authors |
| `GET` | `/api/authors/:authorId` | Get an author and their books |
| `POST` | `/api/authors` | Create an author |
| `PATCH` | `/api/authors/:authorId` | Update an author |
| `DELETE` | `/api/authors/:authorId` | Delete an author without books |

Author body:

```json
{
  "name": "George Orwell"
}
```

### Books

| Method | Route | Result |
| --- | --- | --- |
| `GET` | `/api/books` | List books with their authors |
| `GET` | `/api/books/:bookId` | Get one book with its author |
| `POST` | `/api/books` | Create a book |
| `PATCH` | `/api/books/:bookId` | Update any supplied book fields |
| `DELETE` | `/api/books/:bookId` | Delete a book |

Create-book body:

```json
{
  "title": "1984",
  "publishedYear": 1949,
  "authorId": 1
}
```

`publishedYear` is optional and may be `null`. `title` and `authorId` are required when creating a book. Zod schemas reject unknown properties and invalid types before controller handlers run.

## Example CRUD flow

Create an author first:

```sh
curl -X POST http://localhost:3000/api/authors \
  -H "Authorization: Bearer iot-lab-2026" \
  -H "Content-Type: application/json" \
  -d '{"name":"George Orwell"}'
```

Use the returned author ID to create a book:

```sh
curl -X POST http://localhost:3000/api/books \
  -H "Authorization: Bearer iot-lab-2026" \
  -H "Content-Type: application/json" \
  -d '{"title":"1984","publishedYear":1949,"authorId":1}'
```

Update the book:

```sh
curl -X PATCH http://localhost:3000/api/books/1 \
  -H "Authorization: Bearer iot-lab-2026" \
  -H "Content-Type: application/json" \
  -d '{"publishedYear":1950}'
```

Delete the book before deleting its author:

```sh
curl -X DELETE http://localhost:3000/api/books/1 \
  -H "Authorization: Bearer iot-lab-2026"

curl -X DELETE http://localhost:3000/api/authors/1 \
  -H "Authorization: Bearer iot-lab-2026"
```

## HTTP behavior

- `200 OK`: successful read or update
- `201 Created`: successful creation; includes a `Location` header
- `204 No Content`: successful deletion
- `400 Bad Request`: Zod rejected malformed JSON, unknown fields, invalid types, or invalid IDs
- `401 Unauthorized`: missing or incorrect bearer token
- `404 Not Found`: resource or route does not exist
- `409 Conflict`: author still has books
- `422 Unprocessable Entity`: `authorId` does not reference an author

## Project structure

```text
src/
├── index.ts                 # Starts the Node.js server
├── app.ts                   # Creates the API application
├── controllers/             # HTTP routes, auth, and status codes
├── schemas/                 # Zod v4 request and parameter schemas
├── services/                # Database operations
└── db/
    ├── index.ts             # SQLite connection and foreign-key enforcement
    └── schema.ts            # Drizzle table definitions

drizzle/                     # Generated, versioned SQL migrations
drizzle.config.ts            # Drizzle Kit configuration
```

## Database commands

```sh
npm run db:generate  # Generate SQL after changing the schema
npm run db:migrate   # Apply pending migrations
npm run db:studio    # Open Drizzle Studio
npm run build        # Compile TypeScript
npm start            # Run the compiled server
```
