// 작성자 : 최재우
// 마지막 수정일 : 2025-06-11

export interface IllustrationDTO {
    illustration_id?: number;
    paragraph_id?: number;
    story_id?: number;
    image_url?: string;
    caption_text?: string;
    labels?: string[];
    created_at?: string;
}