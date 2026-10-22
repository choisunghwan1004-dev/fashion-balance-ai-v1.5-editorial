-- 기존 V1 데이터 보존용: schema.sql을 다시 실행하지 않고 이 파일만 실행
USE fashion_balance;
INSERT IGNORE INTO categories(id,name,sort_order) VALUES (7,'가방',7),(8,'벨트',8),(9,'시계',9),(10,'주얼리',10);
ALTER TABLE fashion_items ADD COLUMN shop_url VARCHAR(500) NULL;
-- 이미 shop_url 컬럼이 있다면 위 ALTER 문은 생략하세요.
INSERT INTO users(id,email,password_hash) VALUES(1,'demo@localhost','DEMO_NO_LOGIN') ON DUPLICATE KEY UPDATE email=email;
