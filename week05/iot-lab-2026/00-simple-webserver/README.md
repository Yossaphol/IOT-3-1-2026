# Simple Hono Web Server

Small examples of common Hono features, organized as a reusable student template.

## Setup

```sh
nvm install 24.14.1
nvm use 24.14.1
npm install
copy .env.example .env
npm run dev
```

On macOS or Linux, use `cp .env.example .env` instead of `copy`.

Open <http://localhost:3000>.

## Project structure

```text
src/
├── index.ts              # Starts the Node.js server
├── app.ts                # Creates the Hono app and mounts controllers
├── controllers/
│   ├── books.ts          # Book routes, request validation, auth, responses
│   └── pages.ts          # JSON and HTML page examples
└── services/
    └── books.ts          # Book data and lookup operations
```

Controllers handle HTTP concerns. Services contain data and application logic. `app.ts` only composes the application, while `index.ts` only starts the server.

## Examples

| URL | Hono feature |
| --- | --- |
| <http://localhost:3000/> | JSON response and environment variables |
| <http://localhost:3000/html?name=Student> | HTML helper, dynamic values, and automatic escaping |
| <http://localhost:3000/hello.txt> | Static file middleware |
| <http://localhost:3000/api/books> | Bearer authentication and JSON array response |
| <http://localhost:3000/api/books/1> | Validated route parameter and one JSON object |
| <http://localhost:3000/api/books/999> | `404 Not Found` JSON response |

The book controller protects all its routes. Send the token from `.env` in the standard `Authorization` header:

```sh
curl -H "Authorization: Bearer iot-lab-2026" http://localhost:3000/api/books
```

Book ID behavior:

- Positive integer with a matching book: `200 OK`
- Positive integer without a matching book: `404 Not Found`
- Invalid value such as `abc`, `0`, or `-1`: `400 Bad Request`

## Environment variables

`.env` is required for the API token and is excluded from Git:

```env
NAME=IT KMITL
SECRET_PASSWORD=iot-lab-2026
```

Never commit real API tokens. Restart the server after changing `.env`.

## Build and run

```sh
npm run build
npm start
```

Press `Ctrl+C` to stop the server.
