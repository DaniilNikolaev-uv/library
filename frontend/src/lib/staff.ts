import { apiFetch } from "./api";

export type StaffIssueReader = {
  id: number;
  first_name: string;
  last_name: string;
  card_number: string;
  email: string;
  is_blocked: boolean;
};

export type StaffIssueCopy = {
  id: number;
  inventory_number: string;
  barcode: string | null;
  book_title: string;
  isbn: string | null;
  location_name: string | null;
  location_code: string | null;
};

export type StaffIssueOptions = {
  readers: StaffIssueReader[];
  copies: StaffIssueCopy[];
};

export type StaffDashboardStats = {
  users: number;
  books: number;
  active_loans: number;
  readers: number;
};

export type StaffReturnLoan = {
  id: number;
  status: "active" | "overdue";
  issue_date: string;
  due_date: string;
  reader_id: number;
  reader_card_number: string;
  reader_email: string;
  reader_first_name: string;
  reader_last_name: string;
  copy_id: number;
  inventory_number: string;
  barcode: string | null;
  book_title: string;
  isbn: string | null;
};

export type StaffReturnOptions = {
  loans: StaffReturnLoan[];
};

export async function getDashboardStats() {
  return await apiFetch<StaffDashboardStats>("/api/circulation/loans/dashboard_stats/", {
    method: "GET",
  });
}

export async function getIssueOptions() {
  return await apiFetch<StaffIssueOptions>("/api/circulation/loans/issue_options/", {
    method: "GET",
  });
}

export async function getReturnOptions() {
  return await apiFetch<StaffReturnOptions>("/api/circulation/loans/return_options/", {
    method: "GET",
  });
}

export async function issueLoan(params: {
  copy_id: number;
  reader_id: number;
  loan_days?: number;
}) {
  return await apiFetch(`/api/circulation/loans/issue/`, {
    method: "POST",
    body: JSON.stringify({
      copy: params.copy_id,
      reader: params.reader_id,
      loan_days: params.loan_days,
    }),
  });
}

export async function returnLoan(params: { loan_id: number; mark_lost?: boolean }) {
  return await apiFetch(`/api/circulation/loans/${params.loan_id}/return_book/`, {
    method: "POST",
    body: JSON.stringify({ mark_lost: Boolean(params.mark_lost) }),
  });
}
