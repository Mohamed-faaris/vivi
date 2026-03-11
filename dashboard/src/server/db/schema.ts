import { integer, sqliteTable, text, blob } from "drizzle-orm/sqlite-core";

export const users = sqliteTable("users", (d) => ({
  id: integer({ mode: "number" }).primaryKey({ autoIncrement: true }),
  name: d.text({ length: 256 }).notNull(),
  roll: d.text({ length: 50 }),
  encoding: d.blob(),
  photo: d.text(),
}));

export const attendance = sqliteTable("attendance", (d) => ({
  id: integer({ mode: "number" }).primaryKey({ autoIncrement: true }),
  userId: integer("user_id", { mode: "number" }).references(() => users.id),
  timestamp: d.text({ length: 50 }).notNull(),
  status: d.text({ length: 10 }).notNull(),
  photo: d.text(),
}));
