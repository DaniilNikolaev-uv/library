import { apiFetch } from "./api";

export async function issueLoan(params: {
  copy_id: number;
  reader_id: number;
  loan_days?: number;
}) {
  return await apiFetch(`/api/circulation/loans/issue/`, {
    method: "POST",
    body: JSON.stringify(params),
  });
}

export async function returnLoan(params: { loan_id: number; mark_lost?: boolean }) {
  return await apiFetch(`/api/circulation/loans/${params.loan_id}/return_book/`, {
    method: "POST",
    body: JSON.stringify({ mark_lost: Boolean(params.mark_lost) }),
  });
}

