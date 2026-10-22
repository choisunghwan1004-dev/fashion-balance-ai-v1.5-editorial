CREATE DATABASE IF NOT EXISTS fashion_balance CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE fashion_balance;
CREATE TABLE IF NOT EXISTS users (id INT AUTO_INCREMENT PRIMARY KEY,email VARCHAR(255) NOT NULL UNIQUE,password_hash VARCHAR(255) NOT NULL,created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS categories (id INT AUTO_INCREMENT PRIMARY KEY,name VARCHAR(40) NOT NULL UNIQUE,sort_order INT NOT NULL);
CREATE TABLE IF NOT EXISTS colors (id INT AUTO_INCREMENT PRIMARY KEY,name VARCHAR(40) NOT NULL UNIQUE,hex_code CHAR(7) NOT NULL);
CREATE TABLE IF NOT EXISTS styles (id INT AUTO_INCREMENT PRIMARY KEY,name VARCHAR(40) NOT NULL UNIQUE);
CREATE TABLE IF NOT EXISTS fashion_items (id INT AUTO_INCREMENT PRIMARY KEY,name VARCHAR(120) NOT NULL,category_id INT NOT NULL,color_id INT NOT NULL,style_id INT NOT NULL,season ENUM('봄','여름','가을','겨울','사계절') NOT NULL,price INT NOT NULL,image_url VARCHAR(500),shop_url VARCHAR(500),owner_user_id INT NULL,active BOOLEAN DEFAULT TRUE,FOREIGN KEY(category_id) REFERENCES categories(id),FOREIGN KEY(color_id) REFERENCES colors(id),FOREIGN KEY(style_id) REFERENCES styles(id),FOREIGN KEY(owner_user_id) REFERENCES users(id));
CREATE TABLE IF NOT EXISTS wardrobe_items (id INT AUTO_INCREMENT PRIMARY KEY,user_id INT NOT NULL,item_id INT NOT NULL,UNIQUE KEY uq_wardrobe(user_id,item_id),FOREIGN KEY(user_id) REFERENCES users(id),FOREIGN KEY(item_id) REFERENCES fashion_items(id));
CREATE TABLE IF NOT EXISTS trends (id INT AUTO_INCREMENT PRIMARY KEY,year INT NOT NULL,season ENUM('봄','여름','가을','겨울') NOT NULL,style_id INT NOT NULL,score INT NOT NULL DEFAULT 50,notes TEXT,FOREIGN KEY(style_id) REFERENCES styles(id));
CREATE TABLE IF NOT EXISTS outfits (id INT AUTO_INCREMENT PRIMARY KEY,user_id INT NULL,season VARCHAR(10) NOT NULL,style_id INT NOT NULL,total_price INT NOT NULL,balance_score INT NOT NULL,created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY(user_id) REFERENCES users(id),FOREIGN KEY(style_id) REFERENCES styles(id));
CREATE TABLE IF NOT EXISTS outfit_items (outfit_id INT NOT NULL,item_id INT NOT NULL,PRIMARY KEY(outfit_id,item_id),FOREIGN KEY(outfit_id) REFERENCES outfits(id),FOREIGN KEY(item_id) REFERENCES fashion_items(id));
CREATE TABLE IF NOT EXISTS ratings (id INT AUTO_INCREMENT PRIMARY KEY,outfit_id INT NOT NULL,user_id INT NOT NULL,rating INT NOT NULL CHECK(rating BETWEEN 1 AND 5),FOREIGN KEY(outfit_id) REFERENCES outfits(id),FOREIGN KEY(user_id) REFERENCES users(id));


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


CREATE TABLE IF NOT EXISTS style_profiles (
 user_id INT PRIMARY KEY,
 face_shape ENUM('미선택','둥근형','타원형','각진형','긴형','하트형') NOT NULL DEFAULT '미선택',
 body_shape ENUM('미선택','직선형','상체강조형','하체강조형','허리강조형','균형형','슬림형','보통형','통통형') NOT NULL DEFAULT '미선택',
 undertone ENUM('미선택','웜','쿨','뉴트럴') NOT NULL DEFAULT '미선택',
 preferred_fit ENUM('편안한핏','슬림핏','루즈핏') NOT NULL DEFAULT '편안한핏',
 updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
 FOREIGN KEY (user_id) REFERENCES users(id)
);
