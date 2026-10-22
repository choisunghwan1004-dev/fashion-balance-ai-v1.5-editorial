USE fashion_balance;
-- 기존 값을 유지하며 그림 선택용 3가지 값을 추가합니다. 기존 DB 백업 후 1회 실행하세요.
ALTER TABLE style_profiles MODIFY body_shape ENUM('미선택','직선형','상체강조형','하체강조형','허리강조형','균형형','슬림형','보통형','통통형') NOT NULL DEFAULT '미선택';
