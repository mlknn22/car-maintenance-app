import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, Outlet, useNavigate } from "react-router-dom";
import { getMe } from "../api/auth";
import { clearToken } from "../lib/auth";

export function Layout() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const { data: user } = useQuery({
    queryKey: ["me"],
    queryFn: getMe,
  });

  function handleLogout() {
    clearToken();
    queryClient.clear();
    navigate("/login", { replace: true });
  }

  return (
    <div className="min-h-screen bg-white text-slate-900">
      <header className="border-b border-slate-200">
        <div className="mx-auto flex h-14 max-w-6xl items-center justify-between px-6">
          <Link to="/cars" className="text-sm font-medium tracking-tight">
            CarMaint
          </Link>
          <div className="flex items-center gap-4 text-sm text-slate-500">
            {user && <span>{user.email}</span>}
            <button
              type="button"
              onClick={handleLogout}
              className="rounded-md border border-slate-200 px-3 py-1 text-slate-700 transition hover:bg-slate-50"
            >
              Выйти
            </button>
          </div>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-6 py-8">
        <Outlet />
      </main>
    </div>
  );
}
