import Link from "next/link";

export default function Home() {
  return (
    <div className="space-y-8">
      <section className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-950">
        <h1 className="text-2xl font-semibold tracking-tight">Каталог</h1>
        <p className="mt-2 text-sm text-zinc-600 dark:text-zinc-400">
          Поиск книг, выдачи, бронирования и штрафы — в одном месте.
        </p>
        <div className="mt-4 flex flex-wrap gap-3">
          <Link
            href="/catalog"
            className="rounded-lg bg-zinc-900 px-4 py-2 text-sm font-medium text-white hover:bg-zinc-800 dark:bg-zinc-50 dark:text-black dark:hover:bg-zinc-200"
          >
            Открыть каталог
          </Link>
          <Link
            href="/login"
            className="rounded-lg border border-zinc-200 px-4 py-2 text-sm font-medium hover:bg-zinc-50 dark:border-zinc-800 dark:hover:bg-zinc-900"
          >
            Войти
          </Link>
          <Link
            href="/register"
            className="rounded-lg border border-zinc-200 px-4 py-2 text-sm font-medium hover:bg-zinc-50 dark:border-zinc-800 dark:hover:bg-zinc-900"
          >
            Регистрация
          </Link>
        </div>
      </section>
    </div>
  );
}
