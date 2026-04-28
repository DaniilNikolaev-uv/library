"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useMemo, useState } from "react";

import type { ApiError } from "@/lib/api";
import { getHomeRouteForRole, me } from "@/lib/auth";
import { getReturnOptions, returnLoan, type StaffReturnLoan } from "@/lib/staff";

function normalizeSearchValue(value: string) {
  return value.toLowerCase().replace(/\s+/g, " ").trim();
}

export default function StaffReturnPage() {
  const router = useRouter();
  const [loanId, setLoanId] = useState("");
  const [loanQuery, setLoanQuery] = useState("");
  const [loans, setLoans] = useState<StaffReturnLoan[]>([]);
  const [optionsLoading, setOptionsLoading] = useState(true);
  const [markLost, setMarkLost] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    void (async () => {
      try {
        const user = await me();
        if (user.role !== "librarian" && user.role !== "admin") {
          router.replace(getHomeRouteForRole(user.role));
          return;
        }
        const options = await getReturnOptions();
        setLoans(options.loans);
      } catch {
        router.replace("/login");
      } finally {
        setOptionsLoading(false);
      }
    })();
  }, [router]);

  const filteredLoans = useMemo(() => {
    const query = normalizeSearchValue(loanQuery);
    if (!query) return loans;

    return loans.filter((loan) =>
      [
        String(loan.id),
        loan.reader_first_name,
        loan.reader_last_name,
        `${loan.reader_first_name} ${loan.reader_last_name}`,
        `${loan.reader_last_name} ${loan.reader_first_name}`,
        loan.reader_card_number,
        loan.reader_email,
        loan.book_title,
        loan.inventory_number,
        loan.barcode ?? "",
        loan.isbn ?? "",
      ]
        .map(normalizeSearchValue)
        .some((value) => value.includes(query))
    );
  }, [loanQuery, loans]);

  const selectedLoan = loans.find((loan) => String(loan.id) === loanId) ?? null;

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSuccessMessage(null);
    setLoading(true);
    try {
      await returnLoan({ loan_id: Number(loanId), mark_lost: markLost });
      setSuccessMessage("Успешный возврат!");
      setLoans((current) => current.filter((loan) => String(loan.id) !== loanId));
      setLoanId("");
      setLoanQuery("");
      setMarkLost(false);
    } catch (e) {
      const err = e as ApiError;
      setError(err.detail || "Не удалось оформить возврат");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Возврат</h1>
        </div>
        <Link href="/staff" className="text-sm underline">
          Назад
        </Link>
      </div>

      <form
        onSubmit={onSubmit}
        className="max-w-xl rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-950"
      >
        <div className="grid gap-3">
          <label className="block text-sm">
            <span className="text-zinc-700 dark:text-zinc-300">Поиск выдачи</span>
            <input
              value={loanQuery}
              onChange={(e) => setLoanQuery(e.target.value)}
              className="mt-1 w-full rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-zinc-400 dark:border-zinc-800 dark:bg-black"
              placeholder="По номеру выдачи, читателю, книге, инвентарному номеру, ISBN"
            />
          </label>
          <label className="block text-sm">
            <span className="text-zinc-700 dark:text-zinc-300">Выберите выдачу</span>
            <select
              value={loanId}
              onChange={(e) => setLoanId(e.target.value)}
              className="mt-1 w-full rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-zinc-400 dark:border-zinc-800 dark:bg-black"
              required
              disabled={optionsLoading || loading}
            >
              <option value="">{optionsLoading ? "Загружаем выдачи..." : "Выберите выдачу"}</option>
              {filteredLoans.map((loan) => (
                <option key={loan.id} value={loan.id}>
                  #{loan.id} • {loan.reader_first_name} {loan.reader_last_name} • {loan.book_title} • {loan.inventory_number}
                </option>
              ))}
            </select>
          </label>

          {selectedLoan ? (
            <div className="rounded-lg border border-zinc-200 bg-zinc-50 px-3 py-2 text-sm text-zinc-700 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-300">
              #{selectedLoan.id} • {selectedLoan.reader_first_name} {selectedLoan.reader_last_name} • {selectedLoan.reader_card_number} • {selectedLoan.book_title} • {selectedLoan.inventory_number} • до {selectedLoan.due_date}
            </div>
          ) : null}

          <label className="flex items-center gap-2 text-sm text-zinc-700 dark:text-zinc-300">
            <input
              type="checkbox"
              checked={markLost}
              onChange={(e) => setMarkLost(e.target.checked)}
            />
            Пометить как утерянную
          </label>

          {error ? (
            <div className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-800 dark:border-red-900/40 dark:bg-red-950/40 dark:text-red-200">
              {error}
            </div>
          ) : null}

          {successMessage ? (
            <div className="rounded-lg border border-green-200 bg-green-50 px-3 py-2 text-sm text-green-800 dark:border-green-900/40 dark:bg-green-950/40 dark:text-green-200">
              {successMessage}
            </div>
          ) : null}

          {!optionsLoading && loans.length === 0 ? (
            <div className="rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-800 dark:border-amber-900/40 dark:bg-amber-950/40 dark:text-amber-200">
              Сейчас нет активных или просроченных выдач для возврата.
            </div>
          ) : null}

          <button
            disabled={loading || optionsLoading || !loanId}
            className="rounded-lg bg-zinc-900 px-4 py-2 text-sm font-medium text-white hover:bg-zinc-800 disabled:opacity-60 dark:bg-zinc-50 dark:text-black dark:hover:bg-zinc-200"
          >
            {loading ? "Оформляем..." : "Оформить возврат"}
          </button>
        </div>
      </form>
    </div>
  );
}
