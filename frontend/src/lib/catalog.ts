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

export type Category = {
  id: number;
  name: string;
  parent?: number | null;
};

export type Paginated<T> = {
  count?: number;
  next?: string | null;
  previous?: string | null;
  results?: T[];
} & Record<string, unknown>;

export async function listBooks(
  params?: {
    search?: string;
    category?: string | number;
    year?: string | number;
    available_only?: boolean;
  },
): Promise<Paginated<Book> | Book[]> {
  const qs = new URLSearchParams();
  if (params?.search) qs.set("search", params.search);
  if (params?.category) qs.set("category", String(params.category));
  if (params?.year) qs.set("year", String(params.year));
  if (params?.available_only) qs.set("available_only", "true");
  const suffix = qs.toString() ? `?${qs}` : "";
  return await apiFetch<Paginated<Book> | Book[]>(
    `/api/catalog/books/${suffix}`,
    { method: "GET" },
  );
}

export async function getBook(id: string | number) {
  return await apiFetch<Book>(`/api/catalog/books/${id}/`, { method: "GET" });
}

export async function listCategories(): Promise<Paginated<Category> | Category[]> {
  return await apiFetch<Paginated<Category> | Category[]>("/api/catalog/categories/", {
    method: "GET",
  });
}

