'use client';

import React, { useState } from 'react';
import { Search, Home, Book, Tag, Users, CreditCard, Settings, X, Menu } from 'lucide-react';


const Sidebar = () => {
    const [isSidebarOpen, setIsSidebarOpen] = useState<boolean>(false);

    const toggleSidebar = (): void => {
        setIsSidebarOpen(!isSidebarOpen);
    };
    return (
        <div>
            {/* Mobile Header */}
            <div className="lg:hidden fixed top-0 left-0 right-0 bg-white shadow-sm border-b z-50 h-16">
                <div className="flex items-center justify-between px-4 h-full">
                <button
                    onClick={toggleSidebar}
                    className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                >
                    <Menu className="w-6 h-6 text-gray-600" />
                </button>
                <div className="flex items-center space-x-2">
                    <div className="w-8 h-8 bg-black rounded flex items-center justify-center">
                    <X className="w-5 h-5 text-white" />
                    </div>
                    <span className="font-bold text-lg">Fel-World.AI</span>
                </div>
                <div className="w-10"></div>
                </div>
            </div>

            {/* Overlay for mobile */}
            {isSidebarOpen && (
                <div
                className="lg:hidden fixed inset-0 bg-black bg-opacity-50 z-30"
                onClick={toggleSidebar}
                />
            )}

            {/* Sidebar */}
            <div className={`
                ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
                transition-transform duration-300 ease-in-out
                w-64 bg-white shadow-lg border-r fixed h-screen overflow-y-auto z-40 
            `}>
                {/* Logo - Hidden on mobile (shown in header instead) */}
                <div className="p-4 border-b hidden lg:block">
                <div className="flex items-center space-x-2">
                    <div className="w-8 h-8 bg-black rounded flex items-center justify-center">
                    <X className="w-5 h-5 text-white" />
                    </div>
                    <div>
                    <span className="font-bold text-lg">Fel-World.AI</span>
                    <div className="text-xs text-gray-500">For You</div>
                    </div>
                </div>
                </div>

                {/* Mobile close button */}
                <div className="lg:hidden p-4 border-b">
                <button
                    onClick={toggleSidebar}
                    className="p-2 hover:bg-gray-100 rounded-lg ml-auto block transition-colors"
                >
                    <X className="w-6 h-6 text-gray-600" />
                </button>
                </div>

                {/* Search */}
                <div className="p-4">
                <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                    <input
                    type="text"
                    placeholder="Search for..."
                    className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
                    />
                </div>
                </div>

                {/* Navigation */}
                <nav className="px-4 space-y-1 flex-1 pb-32 lg:pb-20">
                <div className="flex items-center space-x-3 px-3 py-2 text-gray-700 hover:bg-gray-100 rounded-lg cursor-pointer transition-colors">
                    <Home className="w-5 h-5" />
                    <span>Home</span>
                </div>
                <div className="flex items-center space-x-3 px-3 py-2 text-gray-700 hover:bg-gray-100 rounded-lg cursor-pointer transition-colors">
                    <Book className="w-5 h-5" />
                    <span>My Library</span>
                </div>
                <div className="flex items-center space-x-3 px-3 py-2 text-gray-700 hover:bg-gray-100 rounded-lg cursor-pointer transition-colors">
                    <Tag className="w-5 h-5" />
                    <span>Favorite Tag</span>
                </div>
                <div className="flex items-center justify-between px-3 py-2 text-gray-700 hover:bg-gray-100 rounded-lg cursor-pointer transition-colors">
                    <div className="flex items-center space-x-3">
                    <Users className="w-5 h-5" />
                    <span>Friends</span>
                    </div>
                    <span className="bg-blue-500 text-white text-xs px-2 py-1 rounded-full">99+</span>
                </div>
                <div className="flex items-center space-x-3 px-3 py-2 text-gray-700 hover:bg-gray-100 rounded-lg cursor-pointer transition-colors">
                    <CreditCard className="w-5 h-5" />
                    <span>My Subscription</span>
                </div>
                <div className="flex items-center space-x-3 px-3 py-2 text-gray-700 hover:bg-gray-100 rounded-lg cursor-pointer transition-colors">
                    <Settings className="w-5 h-5" />
                    <span>Setting</span>
                </div>
                </nav>

                {/* Bottom buttons */}
                <div className="absolute lg:fixed bottom-4 left-4 right-4 lg:left-4 lg:right-auto lg:w-56 space-y-2 bg-white lg:z-50">
                <button className="w-full py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors">
                    Log In
                </button>
                <button className="w-full py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors">
                    Sign Up Free
                </button>
                </div>
            </div>
        </div>
    )
};

export default Sidebar