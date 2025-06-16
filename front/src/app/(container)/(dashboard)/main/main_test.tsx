// 작성자 : 최재우
// 마지막 수정일 : 2025-06-15
// 마지막 수정 내용 : 

'use client';

import React, { useEffect } from "react";

const Main_test: React.FC = () => {

  
  useEffect(() => {

  }, []);

  return (
    <>
      <div className="w-full h-screen flex justify-around items-center bg-gray-50">
        <div className="div-container flex-1 space-y-4 border">
          <div className="div-container-top border ">
            <div className="div-container-top-inner flex border justify-around">
              <div className="div-container-top-inner-item border">topitem1</div>
              <div className="div-container-top-inner-item border">topitem2</div>
              <div className="div-container-top-inner-item border">topitem3</div>
              <div className="div-container-top-inner-item border">topitem4</div>
              <div className="div-container-top-inner-item border">topitem5</div>
            </div>
          </div>
          <div className="div-container-bottom border">
            <div className="div-container-bottom-inner flex border justify-around">
              <div className="div-container-bottom-inner-item border">bottomitem1</div>
              <div className="div-container-bottom-inner-item border">bottomitem2</div>
              <div className="div-container-bottom-inner-item border">bottomitem3</div>
              <div className="div-container-bottom-inner-item border">bottomitem4</div>
              <div className="div-container-bottom-inner-item border">bottomitem5</div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default Main_test;