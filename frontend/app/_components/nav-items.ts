import type { User } from "@/lib/auth";

export type NavItem = {
  href: string;
  label: string;
  show?: (user: User | null) => boolean;
};

export const mainNavItems: NavItem[] = [
  { href: "/catalog", label: "Каталог" },
  { href: "/reader", label: "Читатель" },
  { href: "/admin", label: "Админ", show: (user) => user?.role === "admin" },
  {
    href: "/staff",
    label: "Сотрудник",
    show: (user) => user?.role === "librarian",
  },
];

export function getVisibleNavItems(user: User | null) {
  return mainNavItems.filter((item) => (item.show ? item.show(user) : true));
}
