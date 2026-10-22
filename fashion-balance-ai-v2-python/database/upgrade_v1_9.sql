USE fashion_balance;
-- Apply once after V1.8. Back up first. Existing demo user 1 remains unclaimed.
ALTER TABLE users ADD COLUMN nickname VARCHAR(60) NULL, ADD COLUMN verified_at DATETIME NULL;
CREATE TABLE auth_links (token_hash CHAR(64) PRIMARY KEY,email VARCHAR(255) NOT NULL,nickname VARCHAR(60) NOT NULL,expires_at DATETIME NOT NULL, INDEX(email));
CREATE TABLE auth_sessions (token_hash CHAR(64) PRIMARY KEY,user_id INT NOT NULL,expires_at DATETIME NOT NULL,FOREIGN KEY(user_id) REFERENCES users(id));
CREATE TABLE auth_limits (bucket CHAR(64) PRIMARY KEY,hits INT NOT NULL DEFAULT 1,expires_at DATETIME NOT NULL);
CREATE TABLE private_photos (filename VARCHAR(80) PRIMARY KEY,user_id INT NOT NULL,FOREIGN KEY(user_id) REFERENCES users(id));
CREATE TABLE recommendation_history (id BIGINT AUTO_INCREMENT PRIMARY KEY,user_id INT NOT NULL,payload JSON NOT NULL,created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY(user_id) REFERENCES users(id),INDEX(user_id,created_at));
