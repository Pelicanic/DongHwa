import React from 'react'
import Sidebar from '@/(components)/Sidebar';


const DashboardWrapper = ({children}: { children: React.ReactNode }) => {
    return (
        <div className="flex min-h-screen bg-gray-50">
            <Sidebar/>
            <main className="flex-1 lg:ml-64 pt-16 lg:pt-0">
                {children}
            </main>
        </div>
    );
}
export default DashboardWrapper