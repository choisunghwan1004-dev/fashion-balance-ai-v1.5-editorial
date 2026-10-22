USE fashion_balance;
INSERT IGNORE INTO categories(id,name,sort_order) VALUES (1,'모자',1),(2,'스카프',2),(3,'아우터',3),(4,'상의',4),(5,'하의',5),(6,'신발',6),(7,'가방',7),(8,'벨트',8),(9,'시계',9),(10,'주얼리',10);
INSERT IGNORE INTO colors(id,name,hex_code) VALUES (1,'베이지','#D5C3A1'),(2,'화이트','#FFFFFF'),(3,'네이비','#22304A'),(4,'브라운','#79543D'),(5,'블랙','#222222'),(6,'그레이','#999999');
INSERT IGNORE INTO styles(id,name) VALUES (1,'스마트 캐주얼'),(2,'미니멀'),(3,'클래식'),(4,'스트리트');
INSERT INTO fashion_items(name,category_id,color_id,style_id,season,price) VALUES
('베이지 캡',1,1,1,'사계절',16000),('브라운 스카프',2,4,1,'가을',14000),('베이지 재킷',3,1,1,'가을',68000),('화이트 티셔츠',4,2,1,'사계절',19000),('네이비 슬랙스',5,3,1,'사계절',39000),('브라운 로퍼',6,4,1,'사계절',42000),
('블랙 캡',1,5,2,'사계절',15000),('그레이 스카프',2,6,2,'겨울',18000),('블랙 재킷',3,5,2,'사계절',62000),('화이트 미니멀 티',4,2,2,'사계절',17000),('그레이 팬츠',5,6,2,'사계절',34000),('블랙 스니커즈',6,5,2,'사계절',41000),
('네이비 캡',1,3,3,'사계절',19000),('베이지 머플러',2,1,3,'겨울',23000),('네이비 코트',3,3,3,'겨울',99000),('화이트 셔츠',4,2,3,'사계절',29000),('베이지 슬랙스',5,1,3,'사계절',42000),('브라운 클래식 슈즈',6,4,3,'사계절',58000),
('블랙 비니',1,5,4,'겨울',14000),('그레이 스트리트 스카프',2,6,4,'겨울',16000),('블랙 점퍼',3,5,4,'겨울',72000),('화이트 오버핏 티',4,2,4,'사계절',21000),('블랙 와이드 팬츠',5,5,4,'사계절',37000),('화이트 스니커즈',6,2,4,'사계절',48000);
INSERT INTO trends(year,season,style_id,score,notes) VALUES (2026,'가을',1,75,'관리자 입력 예시 데이터이며 실제 트렌드 조사 결과가 아닙니다');

-- 예시 사용자(인증 기능 없음) 및 액세서리: 샘플 가격, 실제 판매 상품 아님
INSERT INTO users(id,email,password_hash) VALUES (1,'demo@localhost','DEMO_NO_LOGIN') ON DUPLICATE KEY UPDATE email=email;
INSERT INTO fashion_items(name,category_id,color_id,style_id,season,price) VALUES
('브라운 미니백',7,4,1,'사계절',21000),('브라운 벨트',8,4,1,'사계절',12000),('실버톤 시계',9,6,1,'사계절',25000),('심플 실버톤 주얼리',10,6,1,'사계절',9000),
('블랙 미니백',7,5,2,'사계절',18000),('블랙 벨트',8,5,2,'사계절',11000),('미니멀 시계',9,5,2,'사계절',22000),('미니멀 주얼리',10,2,2,'사계절',8000),
('클래식 가죽 가방',7,4,3,'사계절',35000),('클래식 벨트',8,4,3,'사계절',14000),('클래식 시계',9,3,3,'사계절',32000),('클래식 주얼리',10,1,3,'사계절',13000),
('스트리트 크로스백',7,5,4,'사계절',26000),('스트리트 벨트',8,5,4,'사계절',13000),('스트리트 시계',9,5,4,'사계절',24000),('스트리트 주얼리',10,6,4,'사계절',10000);

INSERT INTO seasonal_looks(season,look_no,title,description,image_url,style_name) VALUES ('봄',1,'라이트 데일리','밝은 상의와 가벼운 재킷','/images/spring_a.webp','스마트 캐주얼') ON DUPLICATE KEY UPDATE title=VALUES(title),description=VALUES(description),image_url=VALUES(image_url),style_name=VALUES(style_name);
INSERT INTO seasonal_looks(season,look_no,title,description,image_url,style_name) VALUES ('봄',2,'소프트 클래식','부드러운 뉴트럴 톤','/images/spring_b.webp','클래식') ON DUPLICATE KEY UPDATE title=VALUES(title),description=VALUES(description),image_url=VALUES(image_url),style_name=VALUES(style_name);
INSERT INTO seasonal_looks(season,look_no,title,description,image_url,style_name) VALUES ('여름',1,'쿨 미니멀','여름용 실제 사진 교체 예정','/images/summer_a.webp','미니멀') ON DUPLICATE KEY UPDATE title=VALUES(title),description=VALUES(description),image_url=VALUES(image_url),style_name=VALUES(style_name);
INSERT INTO seasonal_looks(season,look_no,title,description,image_url,style_name) VALUES ('여름',2,'이지 캐주얼','여름용 실제 사진 교체 예정','/images/summer_b.webp','스마트 캐주얼') ON DUPLICATE KEY UPDATE title=VALUES(title),description=VALUES(description),image_url=VALUES(image_url),style_name=VALUES(style_name);
INSERT INTO seasonal_looks(season,look_no,title,description,image_url,style_name) VALUES ('가을',1,'모던 클래식','베이지와 브라운 레이어드','/images/autumn_a.webp','클래식') ON DUPLICATE KEY UPDATE title=VALUES(title),description=VALUES(description),image_url=VALUES(image_url),style_name=VALUES(style_name);
INSERT INTO seasonal_looks(season,look_no,title,description,image_url,style_name) VALUES ('가을',2,'어반 스트리트','카키 아우터와 데님','/images/autumn_b.webp','스트리트') ON DUPLICATE KEY UPDATE title=VALUES(title),description=VALUES(description),image_url=VALUES(image_url),style_name=VALUES(style_name);
INSERT INTO seasonal_looks(season,look_no,title,description,image_url,style_name) VALUES ('겨울',1,'윈터 클래식','겨울용 실제 사진 교체 예정','/images/winter_a.webp','클래식') ON DUPLICATE KEY UPDATE title=VALUES(title),description=VALUES(description),image_url=VALUES(image_url),style_name=VALUES(style_name);
INSERT INTO seasonal_looks(season,look_no,title,description,image_url,style_name) VALUES ('겨울',2,'윈터 캐주얼','겨울용 실제 사진 교체 예정','/images/winter_b.webp','스마트 캐주얼') ON DUPLICATE KEY UPDATE title=VALUES(title),description=VALUES(description),image_url=VALUES(image_url),style_name=VALUES(style_name);
