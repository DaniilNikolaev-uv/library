"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useMemo, useState } from "react";

import type { ApiError } from "@/lib/api";
import { getHomeRouteForRole, me } from "@/lib/auth";
import { getIssueOptions, issueLoan, type StaffIssueCopy, type StaffIssueReader } from "@/lib/staff";

function normalizeSearchValue(value: string) {
  return value.toLowerCase().replace(/\s+/g, " ").trim();
}

function compactSearchValue(value: string) {
  return normalizeSearchValue(value).replace(/[^a-zа-яё0-9]+/gi, "");
}

export default function StaffIssuePage() {
  const router = useRouter();
  const [copyId, setCopyId] = useState("");
  const [readerId, setReaderId] = useState("");
  const [loanDays, setLoanDays] = useState("");
  const [readerQuery, setReaderQuery] = useState("");
  const [copyQuery, setCopyQuery] = useState("");
  const [readers, setReaders] = useState<StaffIssueReader[]>([]);
  const [copies, setCopies] = useState<StaffIssueCopy[]>([]);
  const [optionsLoading, setOptionsLoading] = useState(true);
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
        const options = await getIssueOptions();
        setReaders(options.readers);
        setCopies(options.copies);
      } catch {
        router.replace("/login");
      } finally {
        setOptionsLoading(false);
      }
    })();
  }, [router]);

  const filteredReaders = useMemo(() => {
    const query = normalizeSearchValue(readerQuery);
    if (!query) return readers;
    const queryCompact = compactSearchValue(readerQuery);
    const queryTokens = query.split(" ").filter(Boolean);

    return readers
      .map((reader) => {
        const fullName = normalizeSearchValue(
          `${reader.first_name} ${reader.last_name}`.trim()
        );
        const reversedName = normalizeSearchValue(
          `${reader.last_name} ${reader.first_name}`.trim()
        );
        const cardNumber = normalizeSearchValue(reader.card_number);
        const email = normalizeSearchValue(reader.email);
        const searchableValues = [fullName, reversedName, cardNumber, email];
        const searchableCompactValues = searchableValues.map(compactSearchValue);

        const matchesAllTokens = queryTokens.every((token) =>
          searchableValues.some((value) => value.includes(token))
        );
        const matchesCompact = queryCompact
          ? searchableCompactValues.some((value) => value.includes(queryCompact))
          : false;

        if (!matchesAllTokens && !matchesCompact) {
          return null;
        }

        let score = 0;
        if (fullName === query || reversedName === query) score += 100;
        if (cardNumber === query || email === query) score += 95;
        if (fullName.startsWith(query) || reversedName.startsWith(query)) score += 60;
        if (email.startsWith(query) || cardNumber.startsWith(query)) score += 50;
        if (matchesCompact) score += 25;
        score += queryTokens.filter((token) =>
          searchableValues.some((value) => value.startsWith(token))
        ).length * 10;

        return { reader, score };
      })
      .filter((item): item is { reader: StaffIssueReader; score: number } => item !== null)
      .sort((a, b) => b.score - a.score || a.reader.last_name.localeCompare(b.reader.last_name))
      .map((item) => item.reader);
  }, [readerQuery, readers]);

  const filteredCopies = useMemo(() => {
    const query = copyQuery.trim().toLowerCase();
    if (!query) return copies;
    return copies.filter((copy) =>
      [
        copy.book_title,
        copy.inventory_number,
        copy.barcode ?? "",
        copy.isbn ?? "",
        copy.location_code ?? "",
        copy.location_name ?? "",
      ]
        .filter(Boolean)
        .some((value) => value.toLowerCase().includes(query))
    );
  }, [copyQuery, copies]);

  const selectedReader = readers.find((reader) => String(reader.id) === readerId) ?? null;
  const selectedCopy = copies.find((copy) => String(copy.id) === copyId) ?? null;

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSuccessMessage(null);
    setLoading(true);
    try {
      await issueLoan({
        copy_id: Number(copyId),
        reader_id: Number(readerId),
        loan_days: loanDays ? Number(loanDays) : undefined,
      });
      setSuccessMessage("Успешно выдано!");
      setCopyId("");
      setReaderId("");
      setLoanDays("");
      setCopyQuery("");
      setReaderQuery("");
    } catch (e) {
      const err = e as ApiError;
      setError(err.detail || "Не удалось оформить выдачу");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Выдача</h1>
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
            <span className="text-zinc-700 dark:text-zinc-300">Читатель</span>
            <input
              value={readerQuery}
              onChange={(e) => setReaderQuery(e.target.value)}
              className="mt-1 w-full rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-zinc-400 dark:border-zinc-800 dark:bg-black"
              placeholder="Поиск по имени, email или номеру билета"
            />
          </label>
          <label className="block text-sm">
            <span className="text-zinc-700 dark:text-zinc-300">Выберите читателя</span>
            <select
              value={readerId}
              onChange={(e) => setReaderId(e.target.value)}
              className="mt-1 w-full rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-zinc-400 dark:border-zinc-800 dark:bg-black"
              required
              disabled={optionsLoading || loading}
            >
              <option value="">{optionsLoading ? "Загружаем читателей..." : "Выберите читателя"}</option>
              {filteredReaders.map((reader) => (
                <option key={reader.id} value={reader.id} disabled={reader.is_blocked}>
                  {reader.first_name} {reader.last_name} • {reader.card_number} • {reader.email}
                  {reader.is_blocked ? " • заблокирован" : ""}
                </option>
              ))}
            </select>
          </label>
          {selectedReader ? (
            <div className="rounded-lg border border-zinc-200 bg-zinc-50 px-3 py-2 text-sm text-zinc-700 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-300">
              {selectedReader.first_name} {selectedReader.last_name} • {selectedReader.card_number} • {selectedReader.email}
            </div>
          ) : null}
          <label className="block text-sm">
            <span className="text-zinc-700 dark:text-zinc-300">Экземпляр книги</span>
            <input
              value={copyQuery}
              onChange={(e) => setCopyQuery(e.target.value)}
              className="mt-1 w-full rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-zinc-400 dark:border-zinc-800 dark:bg-black"
              placeholder="Поиск по названию, инвентарному номеру, ISBN или штрих-коду"
            />
          </label>
          <label className="block text-sm">
            <span className="text-zinc-700 dark:text-zinc-300">Выберите экземпляр</span>
            <select
              value={copyId}
              onChange={(e) => setCopyId(e.target.value)}
              className="mt-1 w-full rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-zinc-400 dark:border-zinc-800 dark:bg-black"
              required
              disabled={optionsLoading || loading}
            >
              <option value="">{optionsLoading ? "Загружаем экземпляры..." : "Выберите экземпляр"}</option>
              {filteredCopies.map((copy) => (
                <option key={copy.id} value={copy.id}>
                  {copy.book_title} • {copy.inventory_number}
                  {copy.location_code ? ` • ${copy.location_code}` : ""}
                </option>
              ))}
            </select>
          </label>
          {selectedCopy ? (
            <div className="rounded-lg border border-zinc-200 bg-zinc-50 px-3 py-2 text-sm text-zinc-700 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-300">
              {selectedCopy.book_title} • {selectedCopy.inventory_number}
              {selectedCopy.location_code ? ` • ${selectedCopy.location_code}` : ""}
              {selectedCopy.isbn ? ` • ISBN ${selectedCopy.isbn}` : ""}
            </div>
          ) : null}
          <label className="block text-sm">
            <span className="text-zinc-700 dark:text-zinc-300">Срок выдачи в днях</span>
            <input
              value={loanDays}
              onChange={(e) => setLoanDays(e.target.value)}
              inputMode="numeric"
              className="mt-1 w-full rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-zinc-400 dark:border-zinc-800 dark:bg-black"
              placeholder="14"
            />
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

          {!optionsLoading && readers.length === 0 ? (
            <div className="rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-800 dark:border-amber-900/40 dark:bg-amber-950/40 dark:text-amber-200">
              В системе нет читателей, которым можно оформить выдачу.
            </div>
          ) : null}

          {!optionsLoading && copies.length === 0 ? (
            <div className="rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-800 dark:border-amber-900/40 dark:bg-amber-950/40 dark:text-amber-200">
              Сейчас нет доступных экземпляров со статусом available.
            </div>
          ) : null}

          <button
            disabled={loading || optionsLoading || !readerId || !copyId}
            className="rounded-lg bg-zinc-900 px-4 py-2 text-sm font-medium text-white hover:bg-zinc-800 disabled:opacity-60 dark:bg-zinc-50 dark:text-black dark:hover:bg-zinc-200"
          >
            {loading ? "Оформляем..." : "Оформить выдачу"}
          </button>
        </div>
      </form>
    </div>
  );
}
