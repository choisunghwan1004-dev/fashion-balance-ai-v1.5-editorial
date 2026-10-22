USE fashion_balance;
CREATE TABLE IF NOT EXISTS seasonal_looks (
 id INT AUTO_INCREMENT PRIMARY KEY,
 season ENUM('봄','여름','가을','겨울') NOT NULL,
 look_no TINYINT NOT NULL,
 title VARCHAR(100) NOT NULL,
 description VARCHAR(250),
 image_url VARCHAR(255) NOT NULL,
 style_name VARCHAR(40) NOT NULL,
 sample_only BOOLEAN NOT NULL DEFAULT TRUE,
 UNIQUE KEY uq_season_look(season,look_no)
);
INSERT INTO seasonal_looks(season,look_no,title,description,image_url,style_name) VALUES ('봄',1,'라이트 데일리','밝은 상의와 가벼운 재킷','/images/spring_a.webp','스마트 캐주얼') ON DUPLICATE KEY UPDATE title=VALUES(title),description=VALUES(description),image_url=VALUES(image_url),style_name=VALUES(style_name);
INSERT INTO seasonal_looks(season,look_no,title,description,image_url,style_name) VALUES ('봄',2,'소프트 클래식','부드러운 뉴트럴 톤','/images/spring_b.webp','클래식') ON DUPLICATE KEY UPDATE title=VALUES(title),description=VALUES(description),image_url=VALUES(image_url),style_name=VALUES(style_name);
INSERT INTO seasonal_looks(season,look_no,title,description,image_url,style_name) VALUES ('여름',1,'쿨 미니멀','여름용 실제 사진 교체 예정','/images/summer_a.webp','미니멀') ON DUPLICATE KEY UPDATE title=VALUES(title),description=VALUES(description),image_url=VALUES(image_url),style_name=VALUES(style_name);
INSERT INTO seasonal_looks(season,look_no,title,description,image_url,style_name) VALUES ('여름',2,'이지 캐주얼','여름용 실제 사진 교체 예정','/images/summer_b.webp','스마트 캐주얼') ON DUPLICATE KEY UPDATE title=VALUES(title),description=VALUES(description),image_url=VALUES(image_url),style_name=VALUES(style_name);
INSERT INTO seasonal_looks(season,look_no,title,description,image_url,style_name) VALUES ('가을',1,'모던 클래식','베이지와 브라운 레이어드','/images/autumn_a.webp','클래식') ON DUPLICATE KEY UPDATE title=VALUES(title),description=VALUES(description),image_url=VALUES(image_url),style_name=VALUES(style_name);
INSERT INTO seasonal_looks(season,look_no,title,description,image_url,style_name) VALUES ('가을',2,'어반 스트리트','카키 아우터와 데님','/images/autumn_b.webp','스트리트') ON DUPLICATE KEY UPDATE title=VALUES(title),description=VALUES(description),image_url=VALUES(image_url),style_name=VALUES(style_name);
INSERT INTO seasonal_looks(season,look_no,title,description,image_url,style_name) VALUES ('겨울',1,'윈터 클래식','겨울용 실제 사진 교체 예정','/images/winter_a.webp','클래식') ON DUPLICATE KEY UPDATE title=VALUES(title),description=VALUES(description),image_url=VALUES(image_url),style_name=VALUES(style_name);
INSERT INTO seasonal_looks(season,look_no,title,description,image_url,style_name) VALUES ('겨울',2,'윈터 캐주얼','겨울용 실제 사진 교체 예정','/images/winter_b.webp','스마트 캐주얼') ON DUPLICATE KEY UPDATE title=VALUES(title),description=VALUES(description),image_url=VALUES(image_url),style_name=VALUES(style_name);
