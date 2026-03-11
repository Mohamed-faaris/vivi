"use server";

import { db } from "~/server/db";
import { users, attendance } from "~/server/db/schema";
import { desc, eq, sql } from "drizzle-orm";

export type AttendanceWithUser = {
  id: number;
  userId: number | null;
  timestamp: string;
  status: string;
  photo: string | null;
  user: {
    id: number;
    name: string;
    roll: string | null;
    photo: string | null;
  } | null;
};

export type DashboardStats = {
  totalUsers: number;
  checkedInToday: number;
  checkedOutToday: number;
};

export async function getDashboardStats(): Promise<DashboardStats> {
  const today = new Date().toISOString().split("T")[0];
  console.log("[Dashboard] Getting stats for date:", today);

  const totalUsersResult = await db.select({ count: sql`count(*)`.as("count") }).from(users);
  const totalUsers = Number(totalUsersResult[0]?.count) ?? 0;
  console.log("[Dashboard] Total users:", totalUsers);

  const checkedInResult = await db
    .select({ count: sql`count(*)`.as("count") })
    .from(attendance)
    .where(sql`${attendance.status} = 'IN' AND ${attendance.timestamp} LIKE ${today + "%"}`);

  const checkedOutResult = await db
    .select({ count: sql`count(*)`.as("count") })
    .from(attendance)
    .where(sql`${attendance.status} = 'OUT' AND ${attendance.timestamp} LIKE ${today + "%"}`);

  const result = {
    totalUsers,
    checkedInToday: Number(checkedInResult[0]?.count) ?? 0,
    checkedOutToday: Number(checkedOutResult[0]?.count) ?? 0,
  };
  
  console.log("[Dashboard] Stats result:", result);
  return result;
}

export async function getTodayAttendance(): Promise<AttendanceWithUser[]> {
  const today = new Date().toISOString().split("T")[0];
  console.log("[Dashboard] Getting attendance for date:", today);

  const results = await db
    .select({
      id: attendance.id,
      userId: attendance.userId,
      timestamp: attendance.timestamp,
      status: attendance.status,
      photo: attendance.photo,
      userIdRef: users.id,
      userName: users.name,
      userRoll: users.roll,
      userPhoto: users.photo,
    })
    .from(attendance)
    .leftJoin(users, eq(attendance.userId, users.id))
    .where(sql`${attendance.timestamp} LIKE ${today + "%"}`)
    .orderBy(desc(attendance.timestamp));

  console.log("[Dashboard] Raw attendance records:", results.length);

  const mapped = results.map((row) => ({
    id: row.id,
    userId: row.userId,
    timestamp: row.timestamp,
    status: row.status,
    photo: row.photo,
    user: row.userIdRef
      ? {
          id: row.userIdRef,
          name: row.userName ?? "Unknown",
          roll: row.userRoll ?? null,
          photo: row.userPhoto ?? null,
        }
      : null,
  }));

  console.log("[Dashboard] Mapped attendance:", mapped);
  return mapped;
}
