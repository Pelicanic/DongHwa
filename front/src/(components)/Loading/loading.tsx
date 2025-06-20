
import React from 'react'
import '@/styles/loading.css'

const Loading = () => {
  return (
    <>  
        <div className="loading">
            <div className="loading-spinner"></div>
            <div className="loading-text">Loading...</div>
        </div>
    </>
  )
}

export default Loading