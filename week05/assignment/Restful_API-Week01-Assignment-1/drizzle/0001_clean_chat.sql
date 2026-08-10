CREATE TABLE "students" (
	"id" integer PRIMARY KEY GENERATED ALWAYS AS IDENTITY (sequence name "students_id_seq" INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START WITH 1 CACHE 1),
	"firstname" text NOT NULL,
	"lastname" text NOT NULL,
	"studentid" integer NOT NULL,
	"birth" date NOT NULL,
	"sex" text NOT NULL
);
--> statement-breakpoint
DROP TABLE "authors" CASCADE;--> statement-breakpoint
DROP TABLE "books" CASCADE;