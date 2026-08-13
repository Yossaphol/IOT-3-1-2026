# PostgreSQL CRUD API with Hono and Drizzle

A deployable REST API using Hono, PostgreSQL, Drizzle ORM, Zod v4, and Vercel Functions.

## My Github reporsitory
https://github.com/Yossaphol/IOT-3-1-2026/tree/main/week05/assignment/Restful_API-Week01-Assignment-1

## Data model

```text
authors (1) ─────< books (many)

books.author_id → authors.id
```

Every book must reference an existing author. PostgreSQL prevents deleting an author while books still reference it.

## Local setup

Start a local PostgreSQL database:

```sh
docker run --name iot-lab-postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=iot_lab \
  -p 5432:5432 \
  -d postgres:17-alpine
```

Install and prepare the project:

```sh
nvm install 24.14.1
nvm use 24.14.1
npm install
copy .env.example .env
npm run db:migrate
```

On macOS or Linux, use `cp .env.example .env` instead of `copy`.

Run the direct Node.js entrypoint:

```sh
npm run dev
```

Or run the Vercel Function entrypoint and `vercel.json` routing locally:

```sh
npm run vercel:dev
```

Use one development command at a time. Both expose the API at <http://localhost:3000/api>.

## Environment variables

```env
SECRET_PASSWORD=iot-lab-2026
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/iot_lab
```

- `SECRET_PASSWORD` protects every `/api/*` route.
- `DATABASE_URL` must be a PostgreSQL connection string.
- Hosted PostgreSQL providers commonly require `sslmode=require` in the URL.
- Never commit `.env` or database credentials.

Every request requires:

```text
Authorization: Bearer iot-lab-2026
Content-Type: application/json
```

## Routes

### Authors

| Method | Route | Result |
| --- | --- | --- |
| `GET` | `/api/authors` | List authors |
| `GET` | `/api/authors/:authorId` | Get an author and their books |
| `POST` | `/api/authors` | Create an author |
| `PATCH` | `/api/authors/:authorId` | Update an author |
| `DELETE` | `/api/authors/:authorId` | Delete an author without books |

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
| `PATCH` | `/api/books/:bookId` | Update supplied book fields |
| `DELETE` | `/api/books/:bookId` | Delete a book |

```json
{
  "title": "1984",
  "publishedYear": 1949,
  "authorId": 1
}
```

`publishedYear` is optional and may be `null`. Zod rejects unknown properties and invalid types before controller handlers run.

## Example request

```sh
curl -X POST http://localhost:3000/api/authors \
  -H "Authorization: Bearer iot-lab-2026" \
  -H "Content-Type: application/json" \
  -d '{"name":"George Orwell"}'
```

## Database commands

```sh
npm run db:generate  # Generate SQL after changing src/db/schema.ts
npm run db:migrate   # Apply pending migrations
npm run db:studio    # Open Drizzle Studio
```

Generated migrations are committed in `drizzle/`. Run migrations against the target database before deploying new application code.

## Deploy to Vercel

1. Create a PostgreSQL database. A PostgreSQL integration from the Vercel Marketplace is suitable.
2. Add `DATABASE_URL` and `SECRET_PASSWORD` to the Vercel project for Production, Preview, and Development as needed.
3. Apply migrations using the production `DATABASE_URL`.
4. Deploy the project.

Using the Vercel CLI:

```sh
npx --yes vercel@latest link
npx --yes vercel@latest env add DATABASE_URL
npx --yes vercel@latest env add SECRET_PASSWORD
npx --yes vercel@latest env pull .env
npm run db:migrate
npx --yes vercel@latest deploy
npx --yes vercel@latest deploy --prod
```

`api/index.ts` is the production Vercel Function entrypoint. `npm run vercel:dev` starts that entrypoint locally through Vercel CLI. `vercel.json` rewrites nested `/api/*` requests to the function while preserving Hono routing. The same `src/app.ts` application is used by the direct Node.js and Vercel entrypoints.

## HTTP behavior

- `200 OK`: successful read or update
- `201 Created`: successful creation with a `Location` header
- `204 No Content`: successful deletion
- `400 Bad Request`: Zod rejected the request
- `401 Unauthorized`: missing or incorrect bearer token
- `404 Not Found`: resource or route does not exist
- `409 Conflict`: author still has books
- `422 Unprocessable Entity`: `authorId` does not reference an author

## Project structure

```text
api/
└── index.ts                 # Vercel Function entrypoint
src/
├── index.ts                 # Direct local Node.js entrypoint
├── app.ts                   # Shared Hono application
├── controllers/             # Routes, auth, and status codes
├── schemas/                 # Zod v4 request schemas
├── services/                # Asynchronous PostgreSQL operations
└── db/
    ├── index.ts             # Shared node-postgres connection pool
    └── schema.ts            # PostgreSQL Drizzle schema

drizzle/                     # Versioned PostgreSQL migrations
drizzle.config.ts            # Drizzle Kit configuration
vercel.json                  # Vercel request rewrites
```
