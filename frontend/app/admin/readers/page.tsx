"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

import type { Reader } from "@/lib/admin";
import { getReaders, updateReader } from "@/lib/admin";

export default function AdminReadersPage() {
  const [readers, setReaders] = useState<Reader[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");

  useEffect(() => {
    loadReaders();
  }, []);

  async function loadReaders() {
    setLoading(true);
    try {
      const data = await getReaders();
      setReaders(data);
    } catch (error) {
      console.error("Failed to load readers:", error);
    } finally {
      setLoading(false);
    }
  }

  async function toggleBlock(reader: Reader) {
    try {
      await updateReader(reader.id, { is_blocked: !reader.is_blocked });
      setReaders(readers.map((r) =>
        r.id === reader.id ? { ...r, is_blocked: !r.is_blocked } : r
      ));
    } catch (error) {
      console.error("Failed to update reader:", error);
      alert("Не удалось обновить");
    }
  }

  const filteredReaders = readers.filter(
    (r) =>
      r.email.toLowerCase().includes(search.toLowerCase()) ||
      r.user.first_name.toLowerCase().includes(search.toLowerCase()) ||
      r.user.last_name.toLowerCase().includes(search.toLowerCase()) ||
      r.card_number.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Читатели</h1>
          <p className="text-sm text-zinc-600 dark:text-zinc-400">
            Управление читателями
          </p>
        </div>
        <Link
          href="/admin"
          className="text-sm text-zinc-600 hover:underline dark:text-zinc-400"
        >
          ← Назад
        </Link>
      </div>

      <div className="flex items-center gap-2">
        <input
          type="text"
          placeholder="Поиск..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-zinc-400 dark:border-zinc-800 dark:bg-black"
        />
      </div>

      {loading ? (
        <div className="py-12 text-center text-zinc-500">Загрузка...</div>
      ) : (
        <div className="overflow-hidden rounded-xl border border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-950">
          <table className="w-full text-sm">
            <thead className="border-b border-zinc-200 bg-zinc-50 dark:border-zinc-800 dark:bg-zinc-900">
              <tr>
                <th className="px-4 py-3 text-left font-medium text-zinc-600 dark:text-zinc-400">
                  Билет
                </th>
                <th className="px-4 py-3 text-left font-medium text-zinc-600 dark:text-zinc-400">
                  ФИО
                </th>
                <th className="px-4 py-3 text-left font-medium text-zinc-600 dark:text-zinc-400">
                  Email
                </th>
                <th className="px-4 py-3 text-left font-medium text-zinc-600 dark:text-zinc-400">
                  Телефон
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
              {filteredReaders.map((reader) => (
                <tr
                  key={reader.id}
                  className="border-b border-zinc-100 last:border-0 dark:border-zinc-900"
                >
                  <td className="px-4 py-3 font-mono text-xs">{reader.card_number}</td>
                  <td className="px-4 py-3">
                    {reader.user.first_name} {reader.user.last_name}
                  </td>
                  <td className="px-4 py-3">{reader.email}</td>
                  <td className="px-4 py-3">{reader.phone_number}</td>
                  <td className="px-4 py-3">
                    {reader.is_blocked ? (
                      <span className="inline-flex items-center rounded-full bg-red-100 px-2.5 py-0.5 text-xs font-medium text-red-800 dark:bg-red-900/40 dark:text-red-200">
                        Заблокирован
                      </span>
                    ) : (
                      <span className="inline-flex items-center rounded-full bg-green-100 px-2.5 py-0.5 text-xs font-medium text-green-800 dark:bg-green-900/40 dark:text-green-200">
                        Активен
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <button
                      onClick={() => toggleBlock(reader)}
                      className={`hover:underline ${reader.is_blocked ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400"}`}
                    >
                      {reader.is_blocked ? "Разблокировать" : "Заблокировать"}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {filteredReaders.length === 0 && (
            <div className="py-12 text-center text-zinc-500">
              Читатели не найдены
            </div>
          )}
        </div>
      )}
    </div>
  );
}
