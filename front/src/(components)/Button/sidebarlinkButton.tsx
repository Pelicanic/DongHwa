// 작성자 : 최재우
// 마지막 수정일 : 2025-06-09
// 마지막 수정 내용 : sidebar 폴더의 index.tsx 파일을 SidebarLink 컴포넌트로 분리

import React from 'react';
import Link from 'next/link';
import { LucideIcon } from 'lucide-react';
import { usePathname } from "next/navigation";


interface SidebarLinkProps {
    href: string;
    icon: LucideIcon;
    label: string;
    isCollapsed?: boolean;
    showLabel?: boolean;
}

const SidebarLink = ({
    href,
    icon: Icon,
    label,
    isCollapsed = false,
    showLabel = true,
}: SidebarLinkProps) => {
    const pathname = usePathname();
    const isActive =
        pathname === href || (pathname === "/" && href === "/");

    return (
        <Link href={href}>
            <div
                className={`
                    flex items-center px-3 py-2 text-gray-700 hover:bg-gray-100 rounded-lg cursor-pointer transition-colors
                    ${isActive ? "bg-blue-200 text-gray-700" : ""}
                    ${isCollapsed ? "justify-center" : "space-x-3"}
                `}
                title={isCollapsed ? label : undefined}
            >
                <Icon className="w-5 h-5" />
                {!isCollapsed && showLabel && (
                    <span className="text-sm font-medium">{label}</span>
                )}
            </div>
        </Link>
    );
};



export default SidebarLink;
