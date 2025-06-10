import React from "react";
import HTMLFlipBook from "react-pageflip";

export default function StorybookPage() {
  return (
    <div className="flex justify-center items-center min-h-screen bg-gradient-to-br from-purple-100 via-pink-100 to-yellow-100">
      <HTMLFlipBook
        width={300}
        height={400}
        size="stretch"
        style={{}}
        startPage={0}
        maxShadowOpacity={0.5}
        drawShadow={true}
        flippingTime={1000}
        usePortrait={true}
        startZIndex={0}
        autoSize={true}
        showCover={true}
        mobileScrollSupport={true}
        minWidth={100}
        maxWidth={500}
        minHeight={100}
        maxHeight={800}
        className="flip-book"
        clickEventForward={true}
        useMouseEvents={true}
        swipeDistance={50}
        showPageCorners={true}
        disableFlipByClick={false}
      >
        <div className="page bg-white p-6">옛날 옛적에...</div>
        <div className="page bg-white p-6">작은 여우가 있었어요 🦊</div>
        <div className="page bg-white p-6">눈 오는 날 길을 잃고...</div>
        <div className="page bg-white p-6">행복하게 마무리되었답니다 💫</div>
      </HTMLFlipBook>
    </div>
  );
}
