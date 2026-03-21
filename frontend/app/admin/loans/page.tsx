"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

import type { Loan } from "@/lib/admin";
import { getLoans, returnLoan } from "@/lib/admin";

export default function AdminLoansPage() {
  const [loans, setLoans] = useState<Loan[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadLoans();
  }, []);

  async function loadLoans() {
    setLoading(true);
    try {
      const data = await getLoans();
      setLoans(data);
    } catch (error) {
      console.error("Failed to load loans:", error);
    } finally {
      setLoading(false);
    }
  }

  async function handleReturn(id: number) {
    if (!confirm("Подтвердить возврат книги?")) return;
    try {
      await returnLoan(id);
      setLoans(loans.map((l) =>
        l.id === id ? { ...l, status: "returned" as const } : l
      ));
    } catch (error) {
      console.error("Failed to return loan:", error);
      alert("Не удалось оформить возврат");
    }
  }

  const activeLoans = loans.filter((l) => l.status === "active" || l.status === "overdue");

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Выдачи</h1>
          <p className="text-sm text-zinc-600 dark:text-zinc-400">
            Активные выдачи книг
          </p>
        </div>
        <Link
          href="/admin"
          className="text-sm text-zinc-600 hover:underline dark:text-zinc-400"
        >
          ← Назад
        </Link>
      </div>

      {loading ? (
        <div className="py-12 text-center text-zinc-500">Загрузка...</div>
      ) : (
        <div className="overflow-hidden rounded-xl border border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-950">
          <table className="w-full text-sm">
            <thead className="border-b border-zinc-200 bg-zinc-50 dark:border-zinc-800 dark:bg-zinc-900">
              <tr>
                <th className="px-4 py-3 text-left font-medium text-zinc-600 dark:text-zinc-400">
                  ID
                </th>
                <th className="px-4 py-3 text-left font-medium text-zinc-600 dark:text-zinc-400">
                  Читатель
                </th>
                <th className="px-4 py-3 text-left font-medium text-zinc-600 dark:text-zinc-400">
                  Выдан
                </th>
                <th className="px-4 py-3 text-left font-medium text-zinc-600 dark:text-zinc-400">
                  Срок
                </th>
                <th className="px-4 py-3 text-left font-medium text-zinc-600 dark:text-zinc-400">
                  Статус
                </th>
                <th className="px-4 py-3 text-right font-medium text-zinc-600 dark:text-zinc-400">
                  Действия
                </th>
              </tr>
            </thead>
            <tbody>
              {activeLoans.map((loan) => (
                <tr
                  key={loan.id}
                  className="border-b border-zinc-100 last:border-0 dark:border-zinc-900"
                >
                  <td className="px-4 py-3 font-mono text-xs">#{loan.id}</td>
                  <td className="px-4 py-3">Reader #{loan.reader}</td>
                  <td className="px-4 py-3">{loan.issue_date}</td>
                  <td className="px-4 py-3">{loan.due_date}</td>
                  <td className="px-4 py-3">
                    <LoanStatusBadge status={loan.status} />
                  </td>
                  <td className="px-4 py-3 text-right">
                    {loan.status === "active" && (
                      <button
                        onClick={() => handleReturn(loan.id)}
                        className="text-blue-600 hover:underline dark:text-blue-400"
                      >
                        Вернуть
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {activeLoans.length === 0 && (
            <div className="py-12 text-center text-zinc-500">
              Активных выдач нет
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function LoanStatusBadge({ status }: { status: string }) {
  const colors: Record<string, string> = {
    active: "bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-200",
    overdue: "bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-200",
    returned: "bg-zinc-100 text-zinc-800 dark:bg-zinc-800 dark:text-zinc-200",
    lost: "bg-zinc-800 text-white dark:bg-zinc-950",
  };
  const labels: Record<string, string> = {
    active: "На руках",
    overdue: "Просрочена",
    returned: "Возвращена",
    lost: "Утеряна",
  };
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${colors[status] || "bg-zinc-100 text-zinc-800"}`}
    >
      {labels[status] || status}
    </span>
  );
}
