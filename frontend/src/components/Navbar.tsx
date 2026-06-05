"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Shield, FileText, Users, Settings, LayoutDashboard, PlusCircle } from "lucide-react";

const links = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/claims", label: "Claims", icon: FileText },
  { href: "/claims/new", label: "New Claim", icon: PlusCircle },
  { href: "/policy", label: "Policy", icon: Shield },
  { href: "/admin", label: "Admin", icon: Settings },
];

export default function Navbar() {
  const pathname = usePathname();
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 backdrop-blur-xl bg-surface/80 border-b border-surface-border">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-3 group">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-plum-600 to-plum-400 flex items-center justify-center shadow-lg shadow-plum-600/20 group-hover:shadow-plum-500/30 transition-shadow">
            <Shield size={20} className="text-white" />
          </div>
          <div>
            <span className="text-lg font-bold gradient-text">ClaimGuard</span>
            <span className="text-[10px] text-text-muted ml-1.5 font-medium">by Plum</span>
          </div>
        </Link>
        <div className="flex items-center gap-1">
          {links.map((l) => {
            const active = pathname === l.href || (l.href !== "/" && pathname.startsWith(l.href));
            return (
              <Link
                key={l.href}
                href={l.href}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                  active
                    ? "bg-plum-600/20 text-plum-300 border border-plum-600/30"
                    : "text-text-secondary hover:text-text-primary hover:bg-surface-elevated"
                }`}
              >
                <l.icon size={16} />
                {l.label}
              </Link>
            );
          })}
        </div>
      </div>
    </nav>
  );
}
