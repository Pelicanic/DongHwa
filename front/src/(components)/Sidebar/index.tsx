import React from 'react';
import { Search, Home, Book, Tag, Users, CreditCard, Settings, X, LucideIcon } from 'lucide-react';
import Link from "next/link";
import { usePathname } from "next/navigation";
import LinkButton from '@/(components)/Button/button';


interface SidebarLinkProps {
    href: string;
    icon: LucideIcon;
    label: string;
}

const SidebarLink = ({
    href,
    icon: Icon,
    label,
}: SidebarLinkProps) => {
    const pathname = usePathname();
    const isActive =
        pathname === href || (pathname === "/" && href === "/");

    return (
        <Link href={href}>
            <div
                className={`
                    flex items-center space-x-3 px-3 py-2 text-gray-700 hover:bg-gray-100 rounded-lg cursor-pointer transition-colors
                    ${isActive ? "bg-blue-200 text-gray-700" : ""}
                `}
            >
                <Icon className="w-5 h-5" />
                <span className="text-sm font-medium">{label}</span>
            </div>
        </Link>
    );
};

interface SidebarProps {
  isSidebarOpen: boolean;
  toggleSidebar: () => void;
}

const Sidebar = ({ isSidebarOpen, toggleSidebar }: SidebarProps) => {
  return (
    <aside
      className={`
        fixed top-0 left-0 z-40 h-screen w-64 bg-white shadow-lg border-r
        transition-transform duration-300 ease-in-out
        ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        lg:translate-x-0
      `}
    >
      <div className="flex flex-col h-full">
        {/* Logo - Hidden on mobile (shown in header instead) */}
        <div className="p-4 border-b hidden lg:block">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-black rounded flex items-center justify-center">
              <X className="w-5 h-5 text-white" />
            </div>
            <div>
              <span className="font-bold text-lg">Pel-World.AI</span>
              <div className="text-right text-xs text-gray-500">For You</div>
            </div>
          </div>
        </div>

        {/* Mobile close button */}
        <div className="p-4 border-b lg:hidden flex justify-end">
          <button
            onClick={toggleSidebar}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-gray-600" />
          </button>
        </div>

        {/* Search */}
        <div className="p-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search for..."
              className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all text-sm"
            />
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-4 pb-4 overflow-y-auto">
          <div className="space-y-1">
            <SidebarLink href="/" icon={Home} label="Home" />
            <SidebarLink href="/overview" icon={Book} label="My Library" />
            <SidebarLink href="/user/favoriteTag" icon={Tag} label="Favorite Tag" />
            <SidebarLink href="/user/friends" icon={Users} label="Friends" />
            <SidebarLink href="/user/mySubscription" icon={CreditCard} label="My Subscription" />
            <SidebarLink href="/user/setting" icon={Settings} label="Setting" />
          </div>
        </nav>

        {/* Bottom buttons */}
        <div className="p-4 space-y-2 border-t bg-white">
          <LinkButton
            className="w-full py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors text-sm font-medium"
            text='Log In'
            href="/user/login"
          />
          <LinkButton
            className="w-full py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors text-sm font-medium"
            text='Sign Up Free'
            href="/user/signup"
          />
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;