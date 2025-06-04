import React from 'react'


const Navbar = () => {
    return (
        <div className="bg-white p-6 shadow-sm">
            {/* <h1 className="text-2xl font-semibold mb-4">Dashboard</h1>
            
            <div className="flex items-center gap-2 justify-between">
            <div ref={navRef} className="flex items-center gap-6 min-w-0 overflow-x-auto scrollbar-hide relative">
                <button 
                onClick={(e) => {
                    e.preventDefault();
                    setActiveTab('overview');
                }}
                className={`pb-2 whitespace-nowrap flex-shrink-0 transition-all ${
                    activeTab === 'overview' 
                    ? 'text-gray-700 font-medium border-b-2 border-gray-700' 
                    : 'text-gray-500 hover:text-gray-700'
                }`}>
                Overview
                </button>
                <button 
                onClick={(e) => {
                    e.preventDefault();
                    setActiveTab('tasks');
                }}
                className={`flex items-center gap-1 pb-2 whitespace-nowrap flex-shrink-0 transition-all ${
                    activeTab === 'tasks'
                    ? 'text-gray-700 font-medium border-b-2 border-gray-700'
                    : 'text-gray-500 hover:text-gray-700'
                }`}>
                Tasks <span className="bg-gray-500 text-white text-xs px-1.5 py-0.5 rounded">2</span>
                </button>
                <button 
                onClick={(e) => {
                    e.preventDefault();
                    setActiveTab('subscriber');
                }}
                className={`flex items-center gap-1 pb-2 whitespace-nowrap flex-shrink-0 transition-all ${
                    activeTab === 'subscriber'
                    ? 'text-gray-700 font-medium border-b-2 border-gray-700'
                    : 'text-gray-500 hover:text-gray-700'
                }`}>
                Subscriber <span className="bg-gray-500 text-white text-xs px-1.5 py-0.5 rounded">3</span>
                </button>
                <button 
                onClick={(e) => {
                    e.preventDefault();
                    setActiveTab('team');
                }}
                className={`flex items-center gap-1 pb-2 whitespace-nowrap flex-shrink-0 transition-all ${
                    activeTab === 'team'
                    ? 'text-gray-700 font-medium border-b-2 border-gray-700'
                    : 'text-gray-500 hover:text-gray-700'
                }`}>
                Team <span className="bg-gray-500 text-white text-xs px-1.5 py-0.5 rounded">99+</span>
                </button>
                <button 
                onClick={(e) => {
                    e.preventDefault();
                    setActiveTab('reports');
                }}
                className={`pb-2 whitespace-nowrap flex-shrink-0 transition-all ${
                    activeTab === 'reports'
                    ? 'text-gray-700 font-medium border-b-2 border-gray-700'
                    : 'text-gray-500 hover:text-gray-700'
                }`}>
                Reports
                </button>
                <button 
                onClick={(e) => {
                    e.preventDefault();
                    setActiveTab('admin');
                }}
                className={`pb-2 whitespace-nowrap flex-shrink-0 transition-all ${
                    activeTab === 'admin'
                    ? 'text-gray-700 font-medium border-b-2 border-gray-700'
                    : 'text-gray-500 hover:text-gray-700'
                }`}>
                Admin
                </button>
                {isOverflowing && (
                <div className="absolute right-0 top-0 bottom-0 w-8 bg-gradient-to-l from-white to-transparent pointer-events-none"></div>
                )}
            </div>
            
            <div className="flex items-center gap-4 flex-shrink-0 pl-4">
                <div className="flex items-center gap-2 text-sm text-gray-600">
                <span>Start date</span>
                <Calendar size={16} />
                </div>
                <ChevronRight size={20} className="text-gray-400" />
                <div className="flex items-center gap-2 text-sm text-gray-600">
                <span>End date</span>
                <Calendar size={16} />
                </div>
            </div>
            </div> */}
        </div>
    )
}

export default Navbar   