import { apiFetch } from "./api";

export type Loan = {
  id: number;
  inventory_number?: string;
  book_title?: string;
  issue_date: string;
  due_date: string;
  return_date?: string | null;
  status: string;
  status_display?: string;
  is_overdue?: boolean;
};

export type Reservation = {
  id: number;
  inventory_number?: string;
  book_title?: string;
  created_at: string;
  expires_at: string;
  status: string;
  status_display?: string;
};

export type Fine = {
  id: number;
  amount: string;
  paid_amount: string;
  status: string;
  status_display?: string;
  paid_at?: string | null;
  inventory_number?: string;
  book_title?: string;
};

type Paginated<T> = { results?: T[] } & Record<string, unknown>;

export async function myLoans(): Promise<Paginated<Loan> | Loan[]> {
  return await apiFetch(`/api/circulation/loans/my/`, { method: "GET" });
}

export async function myReservations(): Promise<Paginated<Reservation> | Reservation[]> {
  return await apiFetch(`/api/reservations/my/`, { method: "GET" });
}

export async function myFines(): Promise<Paginated<Fine> | Fine[]> {
  return await apiFetch(`/api/fines/`, { method: "GET" });
}

