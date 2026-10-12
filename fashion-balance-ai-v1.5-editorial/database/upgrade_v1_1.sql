-- 기존 V1 통합형에서 V1.1로 업데이트 (백업 후 한 번만 실행)
USE fashion_balance;
ALTER TABLE fashion_items ADD COLUMN owner_user_id INT NULL;
ALTER TABLE fashion_items ADD CONSTRAINT fk_fashion_owner FOREIGN KEY (owner_user_id) REFERENCES users(id);
-- NULL: 쇼핑 카탈로그 상품, 1: 데모 사용자가 직접 등록한 개인 의류
-- wardrobe_items에 등록된 카탈로그 상품도 이미 보유 중인 것으로 취급
