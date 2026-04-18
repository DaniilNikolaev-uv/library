import { apiFetch } from "./api";

export type Book = {
  id: number;
  title: string;
  subtitle?: string | null;
  year: number;
  isbn?: string | null;
  language?: string;
  description?: string;
  cover_image?: string | null;
  cover_url?: string | null;
};

export type Paginated<T> = {
  count?: number;
  next?: string | null;
  previous?: string | null;
  results?: T[];
} & Record<string, unknown>;

export async function listBooks(
  params?: { search?: string },
): Promise<Paginated<Book> | Book[]> {
  const qs = new URLSearchParams();
  if (params?.search) qs.set("search", params.search);
  const suffix = qs.toString() ? `?${qs}` : "";
  return await apiFetch<Paginated<Book> | Book[]>(
    `/api/catalog/books/${suffix}`,
    { method: "GET" },
  );
}

export async function getBook(id: string | number) {
  return await apiFetch<Book>(`/api/catalog/books/${id}/`, { method: "GET" });
}

