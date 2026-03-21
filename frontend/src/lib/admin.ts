import { apiFetch } from "./api";

// Types
export type User = {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  role: "admin" | "librarian" | "reader";
  is_active: boolean;
  is_staff: boolean;
};

export type Reader = {
  id: number;
  user: User;
  card_number: string;
  phone_number: string;
  email: string;
  address: string;
  date_registered: string;
  is_blocked: boolean;
};

export type Author = {
  id: number;
  first_name: string;
  last_name: string;
  middle_name: string;
  date_of_birth: string | null;
  date_of_death: string | null;
  description: string;
};

export type Book = {
  id: number;
  title: string;
  subtitle: string | null;
  authors: Author[];
  isbn: string | null;
  year: number;
  categories: number[];
  language: string;
  description: string;
  publisher: number | null;
  cover_image: string | null;
};

export type BookCopy = {
  id: number;
  book: number;
  inventory_number: string;
  barcode: string | null;
  location: number | null;
  status: "available" | "on_loan" | "reserved" | "lost" | "repair" | "written_off";
  acquired_date: string;
  writeoff_date: string | null;
  notes: string;
};

export type Loan = {
  id: number;
  copy: number;
  reader: number;
  issued_by: number;
  issue_date: string;
  due_date: string;
  return_date: string | null;
  status: "active" | "returned" | "overdue" | "lost";
  renewals_count: number;
};

export type Reservation = {
  id: number;
  copy: number;
  reader: number;
  created_at: string;
  expires_at: string;
  status: "active" | "fulfilled" | "cancelled" | "expired";
};

// Users API
export async function getUsers() {
  return await apiFetch<User[]>("/api/admin/users/", { method: "GET" });
}

export async function getUser(id: number) {
  return await apiFetch<User>(`/api/admin/users/${id}/`, { method: "GET" });
}

export async function createUser(data: {
  email: string;
  first_name: string;
  last_name: string;
  password: string;
  role: string;
  is_active: boolean;
  is_staff: boolean;
}) {
  return await apiFetch<User>("/api/admin/users/", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateUser(id: number, data: Partial<User>) {
  return await apiFetch<User>(`/api/admin/users/${id}/`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

export async function deleteUser(id: number) {
  return await apiFetch<void>(`/api/admin/users/${id}/`, {
    method: "DELETE",
  });
}

// Readers API
export async function getReaders() {
  return await apiFetch<Reader[]>("/api/admin/readers/", { method: "GET" });
}

export async function getReader(id: number) {
  return await apiFetch<Reader>(`/api/admin/readers/${id}/`, { method: "GET" });
}

export async function createReader(data: {
  user: number;
  card_number: string;
  phone_number: string;
  email: string;
  address: string;
}) {
  return await apiFetch<Reader>("/api/admin/readers/", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateReader(id: number, data: Partial<Reader>) {
  return await apiFetch<Reader>(`/api/admin/readers/${id}/`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

export async function deleteReader(id: number) {
  return await apiFetch<void>(`/api/admin/readers/${id}/`, {
    method: "DELETE",
  });
}

// Books API
export async function getBooks() {
  return await apiFetch<Book[]>("/api/admin/books/", { method: "GET" });
}

export async function getBook(id: number) {
  return await apiFetch<Book>(`/api/admin/books/${id}/`, { method: "GET" });
}

export async function createBook(data: {
  title: string;
  subtitle?: string;
  authors: number[];
  isbn?: string;
  year: number;
  categories?: number[];
  language?: string;
  description?: string;
  publisher?: number;
}) {
  return await apiFetch<Book>("/api/admin/books/", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateBook(id: number, data: Partial<Book>) {
  return await apiFetch<Book>(`/api/admin/books/${id}/`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

export async function deleteBook(id: number) {
  return await apiFetch<void>(`/api/admin/books/${id}/`, {
    method: "DELETE",
  });
}

// Book Copies API
export async function getBookCopies() {
  return await apiFetch<BookCopy[]>("/api/admin/book-copies/", { method: "GET" });
}

export async function createBookCopy(data: {
  book: number;
  inventory_number: string;
  barcode?: string;
  location?: number;
  status?: string;
  acquired_date: string;
  notes?: string;
}) {
  return await apiFetch<BookCopy>("/api/admin/book-copies/", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateBookCopy(id: number, data: Partial<BookCopy>) {
  return await apiFetch<BookCopy>(`/api/admin/book-copies/${id}/`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

export async function deleteBookCopy(id: number) {
  return await apiFetch<void>(`/api/admin/book-copies/${id}/`, {
    method: "DELETE",
  });
}

// Loans API
export async function getLoans() {
  return await apiFetch<Loan[]>("/api/admin/loans/", { method: "GET" });
}

export async function createLoan(data: {
  copy: number;
  reader: number;
  due_date: string;
}) {
  return await apiFetch<Loan>("/api/admin/loans/", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateLoan(id: number, data: Partial<Loan>) {
  return await apiFetch<Loan>(`/api/admin/loans/${id}/`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

export async function returnLoan(id: number) {
  return await apiFetch<Loan>(`/api/admin/loans/${id}/return_book/`, {
    method: "POST",
  });
}

// Reservations API
export async function getReservations() {
  return await apiFetch<Reservation[]>("/api/admin/reservations/", { method: "GET" });
}

export async function createReservation(data: {
  copy: number;
  reader: number;
}) {
  return await apiFetch<Reservation>("/api/admin/reservations/", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateReservation(id: number, data: Partial<Reservation>) {
  return await apiFetch<Reservation>(`/api/admin/reservations/${id}/`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

export async function cancelReservation(id: number) {
  return await apiFetch<Reservation>(`/api/admin/reservations/${id}/cancel/`, {
    method: "POST",
  });
}
