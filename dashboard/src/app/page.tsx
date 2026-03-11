"use client";

import { useState, useEffect, useTransition } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "~/components/ui/card";
import { Badge } from "~/components/ui/badge";
import { ScrollArea } from "~/components/ui/scroll-area";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "~/components/ui/table";
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
} from "recharts";
import { Users, LogIn, LogOut, Clock, RefreshCw } from "lucide-react";
import { getDashboardStats, getTodayAttendance, type AttendanceWithUser } from "./actions";

function StatsCard({
  title,
  value,
  icon: Icon,
  color,
}: {
  title: string;
  value: number;
  icon: React.ElementType;
  color: string;
}) {
  return (
    <Card className="overflow-hidden border-0 shadow-lg">
      <CardContent className="flex items-center gap-4 p-6">
        <div
          className="flex h-14 w-14 items-center justify-center rounded-2xl"
          style={{ backgroundColor: `${color}15` }}
        >
          <Icon className="h-7 w-7" style={{ color }} />
        </div>
        <div>
          <p className="text-sm font-medium text-muted-foreground">{title}</p>
          <p className="text-3xl font-bold tracking-tight">{value}</p>
        </div>
      </CardContent>
    </Card>
  );
}

function TimeCard() {
  const [time, setTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <Card className="overflow-hidden border-0 shadow-lg">
      <CardContent className="flex items-center gap-4 p-6">
        <div
          className="flex h-14 w-14 items-center justify-center rounded-2xl"
          style={{ backgroundColor: "#f59e0b15" }}
        >
          <Clock className="h-7 w-7" style={{ color: "#f59e0b" }} />
        </div>
        <div>
          <p className="text-sm font-medium text-muted-foreground">Current Time</p>
          <p className="text-2xl font-bold tracking-tight">
            {time.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })}
          </p>
        </div>
      </CardContent>
    </Card>
  );
}

function AttendanceTable({ attendance }: { attendance: AttendanceWithUser[] }) {
  return (
    <Card className="h-full border-0 shadow-lg">
      <CardHeader>
        <CardTitle className="text-xl font-semibold">Today&apos;s Attendance</CardTitle>
        <CardDescription>Real-time attendance log</CardDescription>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-[400px] pr-4">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Roll</TableHead>
                <TableHead>Time</TableHead>
                <TableHead>Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {attendance.map((record) => (
                <TableRow key={record.id}>
                  <TableCell className="font-medium">
                    {record.user?.name ?? "Unknown"}
                  </TableCell>
                  <TableCell className="text-muted-foreground">
                    {record.user?.roll ?? "-"}
                  </TableCell>
                  <TableCell className="text-muted-foreground">
                    {record.timestamp ? new Date(record.timestamp).toLocaleTimeString([], {
                      hour: "2-digit",
                      minute: "2-digit",
                    }) : "-"}
                  </TableCell>
                  <TableCell>
                    <Badge
                      variant={
                        record.status === "IN" ? "default" : "destructive"
                      }
                      className={
                        record.status === "IN"
                          ? "bg-emerald-500 hover:bg-emerald-600"
                          : "bg-rose-500 hover:bg-rose-600"
                      }
                    >
                      {record.status}
                    </Badge>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </ScrollArea>
      </CardContent>
    </Card>
  );
}

function StatusPieChart({ stats }: { stats: { checkedIn: number; checkedOut: number; notChecked: number } }) {
  const data = [
    { name: "Checked In", value: stats.checkedIn, color: "#10b981" },
    { name: "Checked Out", value: stats.checkedOut, color: "#ef4444" },
    { name: "Not Checked", value: stats.notChecked, color: "#6b7280" },
  ];

  return (
    <Card className="border-0 shadow-lg">
      <CardHeader>
        <CardTitle className="text-xl font-semibold">Attendance Status</CardTitle>
        <CardDescription>Today&apos;s breakdown</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="h-[280px]">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={100}
                paddingAngle={4}
                dataKey="value"
              >
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  borderRadius: "8px",
                  border: "none",
                  boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
                }}
              />
              <Legend
                verticalAlign="bottom"
                height={36}
                formatter={(value) => (
                  <span className="text-sm text-muted-foreground">{value}</span>
                )}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}

function HourlyBarChart({ attendance }: { attendance: AttendanceWithUser[] }) {
  const hourlyData: Record<string, { in: number; out: number }> = {};

  attendance.forEach((record) => {
    const hour = record.timestamp ? new Date(record.timestamp).getHours() : 0;
    const key = `${hour}:00`;
    // eslint-disable-next-line @typescript-eslint/prefer-nullish-coalescing
    if (!hourlyData[key]) {
      hourlyData[key] = { in: 0, out: 0 };
    }
    if (record.status === "IN") {
      hourlyData[key].in++;
    } else {
      hourlyData[key].out++;
    }
  });

  const data = Object.entries(hourlyData)
    .map(([hour, counts]) => ({
      hour,
      "Check-ins": counts.in,
      "Check-outs": counts.out,
    }))
    .sort((a, b) => parseInt(a.hour) - parseInt(b.hour));

  return (
    <Card className="border-0 shadow-lg">
      <CardHeader>
        <CardTitle className="text-xl font-semibold">Hourly Activity</CardTitle>
        <CardDescription>Check-ins and check-outs by hour</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="h-[280px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data}>
              <XAxis
                dataKey="hour"
                stroke="#888888"
                fontSize={12}
                tickLine={false}
                axisLine={false}
              />
              <YAxis
                stroke="#888888"
                fontSize={12}
                tickLine={false}
                axisLine={false}
              />
              <Tooltip
                contentStyle={{
                  borderRadius: "8px",
                  border: "none",
                  boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
                }}
              />
              <Legend
                verticalAlign="top"
                height={36}
                formatter={(value) => (
                  <span className="text-sm text-muted-foreground">{value}</span>
                )}
              />
              <Bar dataKey="Check-ins" fill="#10b981" radius={[4, 4, 0, 0]} />
              <Bar dataKey="Check-outs" fill="#ef4444" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}

export default function DashboardPage() {
  const [stats, setStats] = useState<Awaited<ReturnType<typeof getDashboardStats>> | null>(null);
  const [attendance, setAttendance] = useState<AttendanceWithUser[]>([]);
  const [isPending, startTransition] = useTransition();
  const [lastUpdated, setLastUpdated] = useState(new Date());

  const refresh = () => {
    startTransition(async () => {
      const [newStats, newAttendance] = await Promise.all([
        getDashboardStats(),
        getTodayAttendance(),
      ]);
      setStats(newStats);
      setAttendance(newAttendance);
      setLastUpdated(new Date());
    });
  };

  useEffect(() => {
    refresh();
    const interval = setInterval(refresh, 5000);
    return () => clearInterval(interval);
  }, []);

  if (!stats) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  const notChecked = stats.totalUsers - stats.checkedInToday;
  const pieStats = {
    checkedIn: stats.checkedInToday,
    checkedOut: stats.checkedOutToday,
    notChecked: notChecked > 0 ? notChecked : 0,
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950">
      <div className="container mx-auto px-6 py-8">
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold tracking-tight text-slate-900 dark:text-slate-50">
              Attendance Dashboard
            </h1>
            <p className="mt-2 text-lg text-slate-600 dark:text-slate-400">
              Real-time monitoring of attendance records
            </p>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-muted-foreground">
              Last updated: {lastUpdated.toLocaleTimeString()}
            </span>
            <button
              onClick={refresh}
              disabled={isPending}
              className="flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
            >
              <RefreshCw className={`h-4 w-4 ${isPending ? "animate-spin" : ""}`} />
              Refresh
            </button>
          </div>
        </div>

        <div className="mb-8 grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <StatsCard
            title="Total Users"
            value={stats.totalUsers}
            icon={Users}
            color="#6366f1"
          />
          <StatsCard
            title="Checked In Today"
            value={stats.checkedInToday}
            icon={LogIn}
            color="#10b981"
          />
          <StatsCard
            title="Checked Out Today"
            value={stats.checkedOutToday}
            icon={LogOut}
            color="#ef4444"
          />
          <TimeCard />
        </div>

        <div className="mb-8 grid gap-6 lg:grid-cols-2">
          <StatusPieChart stats={pieStats} />
          <HourlyBarChart attendance={attendance} />
        </div>

        <div className="grid gap-6 lg:grid-cols-1">
          <AttendanceTable attendance={attendance} />
        </div>
      </div>
    </div>
  );
}
