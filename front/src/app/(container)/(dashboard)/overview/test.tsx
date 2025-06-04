import React, { useState, useRef, useEffect } from 'react';
import { Home, BookOpen, Heart, Users, Settings, Bell, MoreHorizontal, Calendar, TrendingUp, ChevronRight } from 'lucide-react';

interface CountryData {
  country: string;
  flag: string;
  percentage: string;
  users: string;
}

interface UserData {
  name: string;
  amount: string;
  change: string;
  positive: boolean;
}

const MyLibrary: React.FC = () => {
  const [isOverflowing, setIsOverflowing] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<string>('overview');
  const navRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const checkOverflow = () => {
      if (navRef.current) {
        setIsOverflowing(navRef.current.scrollWidth > navRef.current.clientWidth);
      }
    };

    checkOverflow();
    window.addEventListener('resize', checkOverflow);
    return () => window.removeEventListener('resize', checkOverflow);
  }, []);

  // Donut chart image component
  const DonutChart: React.FC<{ percentage: number; size?: number; className?: string }> = ({ 
    percentage, 
    size = 120, 
    className = "" 
  }) => {
    return (
      <div className={`relative ${className}`} style={{ width: size, height: size }}>
        <img 
          src="https://via.placeholder.com/120x120/e5e7eb/6b7280?text=67%25" 
          alt={`Chart showing ${percentage}%`}
          className="w-full h-full rounded-full"
        />
      </div>
    );
  };

  // Pie chart image component
  const PieChart: React.FC = () => {
    return (
      <div className="w-full h-full max-w-[200px] max-h-[200px] mx-auto">
        <img 
          src="https://via.placeholder.com/200x200/e5e7eb/6b7280?text=Pie+Chart" 
          alt="Account types pie chart"
          className="w-full h-full rounded-full"
        />
      </div>
    );
  };

  // World map image component
  const WorldMap: React.FC = () => {
    return (
      <div className="relative w-full h-48 bg-gray-100 rounded-lg overflow-hidden">
        <img 
          src="https://via.placeholder.com/600x200/f3f4f6/6b7280?text=World+Map" 
          alt="World Map" 
          className="w-full h-full object-cover"
        />
        <div className="absolute bottom-4 right-4 bg-gray-900 text-white p-3 rounded-lg">
          <p className="text-xs mb-2">선택한 국가 내 모든 유저와 실호적음</p>
          <div className="flex gap-2">
            <button className="text-xs px-3 py-1 bg-gray-700 rounded hover:bg-gray-600 transition-colors">
              Link Action
            </button>
            <button className="text-xs px-3 py-1 bg-blue-600 rounded hover:bg-blue-700 transition-colors">
              Button
            </button>
          </div>
        </div>
      </div>
    );
  };

  const countryData: CountryData[] = [
    { country: 'United States', flag: '🇺🇸', percentage: '27.5%', users: '4.5M' },
    { country: 'Australia', flag: '🇦🇺', percentage: '11.2%', users: '2.3M' },
    { country: 'China', flag: '🇨🇳', percentage: '9.4%', users: '2M' },
    { country: 'Germany', flag: '🇩🇪', percentage: '8%', users: '1.7M' },
    { country: 'Romania', flag: '🇷🇴', percentage: '7.9%', users: '1.6M' },
    { country: 'Japan', flag: '🇯🇵', percentage: '6.1%', users: '1.2M' },
    { country: 'Netherlands', flag: '🇳🇱', percentage: '5.9%', users: '1M' },
  ];

  const userData: UserData[] = [
    { name: 'User Name', amount: '$1.2M', change: '+8.2%', positive: true },
    { name: 'User Name', amount: '$800K', change: '+7%', positive: true },
    { name: 'User Name', amount: '$645K', change: '+2.5%', positive: true },
    { name: 'User Name', amount: '$590K', change: '-6.5%', positive: false },
    { name: 'User Name', amount: '$342K', change: '+1.7%', positive: true },
  ];

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="w-64 bg-gray-50 border-r border-gray-200">
        <div className="p-4">
          {/* Logo Section */}
          <div className="flex items-center gap-2 mb-6">
            <div className="w-8 h-8 bg-gray-300 rounded flex items-center justify-center">
              <span className="text-gray-600 font-bold text-sm">X</span>
            </div>
            <div className="flex flex-col items-center">
              <span className="font-semibold text-gray-800 text-lg">Fel-World.AI</span>
              <span className="text-xs text-gray-500">for Figma</span>
            </div>
          </div>
          
          {/* User Icons */}
          <div className="flex items-center justify-center gap-4 mb-6">
            <button 
              onClick={() => console.log('Profile clicked')}
              className="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center hover:bg-gray-300 transition-colors">
              <Users size={18} className="text-gray-500" />
            </button>
            <button 
              onClick={() => console.log('Settings clicked')}
              className="w-10 h-10 rounded-full flex items-center justify-center border-2 border-gray-300 hover:border-gray-400 hover:bg-gray-50 transition-colors">
              <Settings size={18} className="text-gray-600" />
            </button>
            <button 
              onClick={() => console.log('Notifications clicked')}
              className="relative w-10 h-10 rounded-full flex items-center justify-center border-2 border-gray-300 hover:border-gray-400 hover:bg-gray-50 transition-colors">
              <Bell size={18} className="text-gray-600" />
              <div className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 rounded-full flex items-center justify-center">
                <span className="text-xs text-white">1</span>
              </div>
            </button>
          </div>
          
          {/* Search Bar */}
          <div className="mb-6">
            <div className="relative">
              <input 
                type="text" 
                placeholder="Search for..." 
                className="w-full pl-10 pr-3 py-2.5 bg-white border border-gray-200 rounded-lg text-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <svg className="absolute left-3 top-3 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
          </div>

          {/* Navigation Menu */}
          <nav className="space-y-1">
            <button 
              onClick={() => console.log('Home clicked')}
              className="flex items-center gap-3 px-3 py-2.5 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors w-full text-left">
              <Home size={20} strokeWidth={1.5} />
              <span className="font-medium">Home</span>
            </button>
            <button 
              onClick={() => console.log('My Library clicked')}
              className="flex items-center gap-3 px-3 py-2.5 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors w-full text-left">
              <BookOpen size={20} strokeWidth={1.5} />
              <span className="font-medium">My Library</span>
            </button>
            <button 
              onClick={() => console.log('Favorite Tage clicked')}
              className="flex items-center gap-3 px-3 py-2.5 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors w-full text-left">
              <Heart size={20} strokeWidth={1.5} />
              <span className="font-medium">Favorite Tage</span>
            </button>
            <button 
              onClick={() => console.log('Friends clicked')}
              className="flex items-center gap-3 px-3 py-2.5 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors w-full text-left">
              <Users size={20} strokeWidth={1.5} />
              <span className="font-medium">Friends</span>
            </button>
            <button 
              onClick={() => console.log('My Subscription clicked')}
              className="flex items-center gap-3 px-3 py-2.5 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors w-full text-left">
              <BookOpen size={20} strokeWidth={1.5} />
              <span className="font-medium">My Subscription</span>
            </button>
            <button 
              onClick={() => console.log('Setting clicked')}
              className="flex items-center gap-3 px-3 py-2.5 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors w-full text-left">
              <Settings size={20} strokeWidth={1.5} />
              <span className="font-medium">Setting</span>
              <div className="ml-auto flex items-center gap-1">
                <span className="text-xs bg-gray-500 text-white px-2 py-0.5 rounded-full">99+</span>
                <ChevronRight size={16} className="text-gray-400 transform rotate-90" />
              </div>
            </button>
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-auto">
        {/* Header */}
        <div className="bg-white p-6 shadow-sm">
          <h1 className="text-2xl font-semibold mb-4">Dashboard</h1>
          
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
          </div>
        </div>

        {/* Dashboard Grid */}
        <div className="p-6">
          <div className="grid grid-cols-4 gap-6">
            {/* Stats Cards */}
            <div className="bg-white p-6 rounded-lg shadow-sm">
              <p className="text-gray-500 text-sm mb-2">Users Total</p>
              <p className="text-3xl font-bold">11.8M</p>
              <p className="text-green-500 text-sm mt-1">+2.5%</p>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow-sm">
              <p className="text-gray-500 text-sm mb-2">New Users</p>
              <p className="text-3xl font-bold">8.236K</p>
              <p className="text-gray-500 text-sm mt-1 bg-gray-200 inline-block px-2 py-0.5 rounded">-1.2%</p>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow-sm">
              <p className="text-gray-500 text-sm mb-2">Active Users</p>
              <p className="text-3xl font-bold">2.352M</p>
              <p className="text-green-500 text-sm mt-1">+11%</p>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow-sm">
              <p className="text-gray-500 text-sm mb-2">New Users</p>
              <p className="text-3xl font-bold">8K</p>
              <p className="text-green-500 text-sm mt-1">+5.2%</p>
            </div>

            {/* Target Chart */}
            <div className="bg-white p-6 rounded-lg shadow-sm">
              <h3 className="font-semibold mb-4">Target</h3>
              <div className="flex justify-start gap-6 mb-4 text-sm">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-gray-600 rounded-full"></div>
                  <span className="text-gray-600">Achieved</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-gray-300 rounded-full"></div>
                  <span className="text-gray-600">Remaining</span>
                </div>
              </div>
              <div className="flex items-center justify-center">
                <DonutChart percentage={67} size={140} />
              </div>
            </div>

            {/* Most Active Account Types */}
            <div className="bg-white p-6 rounded-lg shadow-sm">
              <h3 className="font-semibold mb-4">Most Active Account Types</h3>
              <div className="flex items-center justify-center">
                <PieChart />
              </div>
              <div className="flex justify-center gap-6 mt-4 text-sm">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-gray-600 rounded-full"></div>
                  <span className="text-gray-600">Very Active</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-gray-300 rounded-full"></div>
                  <span className="text-gray-600">Inactive</span>
                </div>
              </div>
            </div>

            {/* Active Countries */}
            <div className="bg-white p-6 rounded-lg shadow-sm col-span-2">
              <h3 className="font-semibold mb-4">Active Countries</h3>
              <WorldMap />
              <div className="flex justify-center gap-6 mt-4 text-sm">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-gray-600 rounded-full"></div>
                  <span className="text-gray-600">Very Active</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-gray-300 rounded-full"></div>
                  <span className="text-gray-600">Inactive</span>
                </div>
              </div>
            </div>

            {/* Users by Country */}
            <div className="bg-white p-6 rounded-lg shadow-sm col-span-2">
              <h3 className="font-semibold mb-4">Users by Country</h3>
              <div className="space-y-3">
                {countryData.map((item, index) => (
                  <div key={index} className="flex items-center gap-3">
                    <span className="text-lg">{item.flag}</span>
                    <span className="text-sm flex-1">{item.country}</span>
                    <span className="text-sm text-gray-600">{item.percentage}</span>
                    <span className="text-sm text-gray-600">{item.users}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Top 5 Best Buying Users */}
            <div className="bg-white p-6 rounded-lg shadow-sm col-span-2">
              <h3 className="font-semibold mb-4">Top 5 Best Buying Users</h3>
              <div className="flex items-center justify-center mb-4">
                <DonutChart percentage={75} size={150} />
              </div>
              <div className="space-y-3">
                {userData.map((user, index) => (
                  <div key={index} className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-gray-300 rounded-full"></div>
                    <span className="text-sm flex-1">{user.name}</span>
                    <span className="text-sm font-medium">{user.amount}</span>
                    <span className={`text-sm ${user.positive ? 'text-green-500' : 'text-red-500 bg-gray-200 px-2 py-0.5 rounded'}`}>
                      {user.change}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MyLibrary;