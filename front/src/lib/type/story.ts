
// lib/types/story.ts
// 작성자 : 최재우
// 마지막 수정일 : 2025-06-11

export interface storyDTO {
    story_id?: string | number;
    author_user?: string | number;
    title?: string;
    created_at?: string; 
    updated_at?: string;
    status?: string;
    age?: string;
    summary?: string;
    author_name?: string;
    cover_img?: string;
}

