USE fashion_balance;
CREATE TABLE IF NOT EXISTS style_profiles (
 user_id INT PRIMARY KEY,
 face_shape ENUM('미선택','둥근형','타원형','각진형','긴형','하트형') NOT NULL DEFAULT '미선택',
 body_shape ENUM('미선택','직선형','상체강조형','하체강조형','허리강조형','균형형') NOT NULL DEFAULT '미선택',
 undertone ENUM('미선택','웜','쿨','뉴트럴') NOT NULL DEFAULT '미선택',
 preferred_fit ENUM('편안한핏','슬림핏','루즈핏') NOT NULL DEFAULT '편안한핏',
 updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
 FOREIGN KEY (user_id) REFERENCES users(id)
);
