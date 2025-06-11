// 작성자 : 최재우
// 마지막 수정일 : 2025-06-11

export interface auth_userDTO {
    id? : number;
    password? : string;
    last_login? : string | null;
    is_superuser? : boolean;
    username? : string;
    first_name? : string;
    last_name? : string;
    email? : string;
    is_staff? : boolean;
    is_active? : boolean;
    date_joined? : string;
}