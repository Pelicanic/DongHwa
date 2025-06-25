// 배경음악 매핑
export const MUSIC_MAPPING = {
  "밝은": "fairy tale(Bright).mp3",
  "따뜻한": "fairy tale(Warm).mp3", 
  "슬픈": "fairy tale(Sad).mp3",
  "신비로운": "fairy tale(Mythical).mp3",
  "무서운": "fairy tale(Scary).mp3"
} as const;

// 기분에 따른 배경음악 파일명 반환
export const getMusicFile = (mood: string): string => {
  return MUSIC_MAPPING[mood as keyof typeof MUSIC_MAPPING] || MUSIC_MAPPING["밝은"];
};

// DB에서 기분 추출 함수
export const extractMoodFromQuestionText = (questionText: string): string => {
  const moodMatch = questionText.match(/(?:Mood:|\[Mood\]\s*:)\s*([^,]+)/i);
  return moodMatch && moodMatch[1] ? moodMatch[1].trim() : '밝은';
};

// 배경음악 설정 및 재생 함수
export const setupBackgroundMusic = (
  mood: string,
  volume: number = 0.3,
  onSuccess?: () => void,
  onError?: (error: any) => void
): HTMLAudioElement | null => {
  try {
    const musicFile = getMusicFile(mood);
    const audio = new Audio(`/bgsound/${musicFile}`);
    audio.loop = true;
    audio.volume = volume;
    
    const playPromise = audio.play();
    
    if (playPromise !== undefined) {
      playPromise
        .then(() => {
          onSuccess?.();
        })
        .catch(error => {
          onError?.(error);
          // 자동재생이 차단된 경우를 위한 이벤트 리스너 추가
          const handleFirstUserInteraction = () => {
            audio.play().catch(err => {
              console.log('사용자 상호작용 후에도 재생 실패:', err);
            });
            // 이벤트 리스너 제거 (한 번만 실행)
            document.removeEventListener('click', handleFirstUserInteraction);
            document.removeEventListener('keydown', handleFirstUserInteraction);
            document.removeEventListener('touchstart', handleFirstUserInteraction);
          };
          
          // 다양한 사용자 상호작용 이벤트 리스너 추가
          document.addEventListener('click', handleFirstUserInteraction, { once: true });
          document.addEventListener('keydown', handleFirstUserInteraction, { once: true });
          document.addEventListener('touchstart', handleFirstUserInteraction, { once: true });
        });
    }
    
    return audio;
  } catch (error) {
    console.error('배경음악 설정 오류:', error);
    return null;
  }
};
