"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useMemo, useState } from "react";

import type { ApiError } from "@/lib/api";
import type { AuditLog } from "@/lib/admin";
import { getAuditLogs } from "@/lib/admin";
import { useAuth } from "@/lib/auth-context";

const ACTION_LABELS: Record<string, string> = {
  create: "Создание",
  update: "Изменение",
  delete: "Удаление",
  issue: "Выдача",
  return: "Возврат",
  renew: "Продление",
  reserve: "Бронь",
  cancel_reservation: "Отмена брони",
  pay_fine: "Оплата штрафа",
};

export default function AdminAuditPage() {
  const router = useRouter();
  const { user, loading } = useAuth();
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [search, setSearch] = useState("");
  const [action, setAction] = useState("");
  const [entityType, setEntityType] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!loading && (!user || user.role !== "admin")) {
      router.push("/login");
    }
  }, [user, loading, router]);

  async function loadLogs() {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getAuditLogs({
        action: action || undefined,
        entity_type: entityType || undefined,
        search: search.trim() || undefined,
      });
      setLogs(data);
    } catch (e) {
      const err = e as ApiError;
      setError(err.detail || "Не удалось загрузить аудит");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    if (user?.role === "admin") {
      void loadLogs();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user]);

  const entityTypes = useMemo(() => {
    return Array.from(new Set(logs.map((item) => item.entity_type))).sort();
  }, [logs]);

  if (loading || !user || user.role !== "admin") {
    return null;
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Audit Timeline</h1>
          <p className="text-sm text-zinc-600 dark:text-zinc-400">
            Лента ключевых действий по системе
          </p>
        </div>
        <Link
          href="/admin"
          className="text-sm text-zinc-600 hover:underline dark:text-zinc-400"
        >
          ← Назад
        </Link>
      </div>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          void loadLogs();
        }}
        className="flex flex-wrap gap-2"
      >
        <input
          type="text"
          placeholder="Поиск по сущности, ID, email..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="min-w-72 flex-1 rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-zinc-400 dark:border-zinc-800 dark:bg-black"
        />
        <select
          value={action}
          onChange={(e) => setAction(e.target.value)}
          className="rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-zinc-400 dark:border-zinc-800 dark:bg-black"
        >
          <option value="">Все действия</option>
          {Object.entries(ACTION_LABELS).map(([value, label]) => (
            <option key={value} value={value}>
              {label}
            </option>
          ))}
        </select>
        <select
          value={entityType}
          onChange={(e) => setEntityType(e.target.value)}
          className="rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-zinc-400 dark:border-zinc-800 dark:bg-black"
        >
          <option value="">Все сущности</option>
          {entityTypes.map((value) => (
            <option key={value} value={value}>
              {value}
            </option>
          ))}
        </select>
        <button
          disabled={isLoading}
          className="rounded-lg bg-zinc-900 px-4 py-2 text-sm font-medium text-white hover:bg-zinc-800 disabled:opacity-60 dark:bg-zinc-50 dark:text-black dark:hover:bg-zinc-200"
        >
          {isLoading ? "..." : "Применить"}
        </button>
      </form>

      {error ? (
        <div className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-800 dark:border-red-900/40 dark:bg-red-950/40 dark:text-red-200">
          {error}
        </div>
      ) : null}

      <div className="space-y-3">
        {logs.map((log) => (
          <article
            key={log.id}
            className="rounded-xl border border-zinc-200 bg-white p-4 shadow-sm dark:border-zinc-800 dark:bg-zinc-950"
          >
            <div className="flex flex-wrap items-center gap-2">
              <ActionBadge action={log.action} />
              <span className="text-sm font-medium">
                {log.entity_type} #{log.entity_id}
              </span>
              <span className="text-sm text-zinc-500 dark:text-zinc-400">
                {new Date(log.timestamp).toLocaleString("ru-RU")}
              </span>
            </div>

            <div className="mt-2 text-sm text-zinc-600 dark:text-zinc-400">
              Пользователь: {log.user_email || "Системное событие"}
            </div>

            {(log.data_before || log.data_after) && (
              <div className="mt-3 grid gap-3 lg:grid-cols-2">
                <div className="rounded-lg bg-zinc-50 p-3 dark:bg-zinc-900">
                  <div className="mb-2 text-xs font-medium uppercase tracking-wide text-zinc-500">
                    До
                  </div>
                  <pre className="overflow-x-auto whitespace-pre-wrap text-xs text-zinc-700 dark:text-zinc-300">
                    {JSON.stringify(log.data_before ?? {}, null, 2)}
                  </pre>
                </div>
                <div className="rounded-lg bg-zinc-50 p-3 dark:bg-zinc-900">
                  <div className="mb-2 text-xs font-medium uppercase tracking-wide text-zinc-500">
                    После
                  </div>
                  <pre className="overflow-x-auto whitespace-pre-wrap text-xs text-zinc-700 dark:text-zinc-300">
                    {JSON.stringify(log.data_after ?? {}, null, 2)}
                  </pre>
                </div>
              </div>
            )}
          </article>
        ))}

        {!isLoading && logs.length === 0 ? (
          <div className="py-12 text-center text-zinc-500">События не найдены</div>
        ) : null}
      </div>
    </div>
  );
}

function ActionBadge({ action }: { action: string }) {
  const colors: Record<string, string> = {
    create: "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-200",
    update: "bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-200",
    delete: "bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-200",
    issue: "bg-violet-100 text-violet-800 dark:bg-violet-900/40 dark:text-violet-200",
    return: "bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-200",
    renew: "bg-cyan-100 text-cyan-800 dark:bg-cyan-900/40 dark:text-cyan-200",
    reserve: "bg-fuchsia-100 text-fuchsia-800 dark:bg-fuchsia-900/40 dark:text-fuchsia-200",
    cancel_reservation:
      "bg-orange-100 text-orange-800 dark:bg-orange-900/40 dark:text-orange-200",
    pay_fine: "bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-200",
  };

  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${colors[action] || "bg-zinc-100 text-zinc-800 dark:bg-zinc-800 dark:text-zinc-200"}`}
    >
      {ACTION_LABELS[action] || action}
    </span>
  );
}
