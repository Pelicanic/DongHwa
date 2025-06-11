
// 작성자 : 최재우
// 마지막 수정일 : 2025-06-11

export interface UserDTO {
    user_id?: number;
    login_id?: string;
    password_hash?: string;
    name?: string;
    nickname?: string;
    email?: string;
    age?: number;
    interests?: string[];
    created_at?: string;
    last_login?: string | null;
    profile_image_url?: string;
    provider?: string; // e.g., 'local', 'google', 'kakao'
    provider_id?: string; // ID from the provider
    is_active?: boolean;
    email_verification_token?: string | null; // Token for email verification
}