# DB 설계·데이터 사전

MySQL 8 / utf8mb4. V1.8 기본 schema와 V1.9 인증 확장을 실제 SQL에서 추출했습니다. V2.1의 추가 테이블 변경은 없습니다. V1.9 적용 완료 DB에는 추가 DDL이 필요하지 않습니다.

## users

| 컬럼/제약 | 실제 정의 |
|---|---|
| `id` | `id INT AUTO_INCREMENT PRIMARY KEY` |
| `email` | `email VARCHAR(255) NOT NULL UNIQUE` |
| `password_hash` | `password_hash VARCHAR(255) NOT NULL` |
| `created_at` | `created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP` |
| `nickname` | `nickname VARCHAR(60) NULL` |
| `verified_at` | `verified_at DATETIME NULL` |

## categories

| 컬럼/제약 | 실제 정의 |
|---|---|
| `id` | `id INT AUTO_INCREMENT PRIMARY KEY` |
| `name` | `name VARCHAR(40) NOT NULL UNIQUE` |
| `sort_order` | `sort_order INT NOT NULL` |

## colors

| 컬럼/제약 | 실제 정의 |
|---|---|
| `id` | `id INT AUTO_INCREMENT PRIMARY KEY` |
| `name` | `name VARCHAR(40) NOT NULL UNIQUE` |
| `hex_code` | `hex_code CHAR(7) NOT NULL` |

## styles

| 컬럼/제약 | 실제 정의 |
|---|---|
| `id` | `id INT AUTO_INCREMENT PRIMARY KEY` |
| `name` | `name VARCHAR(40) NOT NULL UNIQUE` |

## fashion_items

| 컬럼/제약 | 실제 정의 |
|---|---|
| `id` | `id INT AUTO_INCREMENT PRIMARY KEY` |
| `name` | `name VARCHAR(120) NOT NULL` |
| `category_id` | `category_id INT NOT NULL` |
| `color_id` | `color_id INT NOT NULL` |
| `style_id` | `style_id INT NOT NULL` |
| `season` | `season ENUM('봄','여름','가을','겨울','사계절') NOT NULL` |
| `price` | `price INT NOT NULL` |
| `image_url` | `image_url VARCHAR(500)` |
| `shop_url` | `shop_url VARCHAR(500)` |
| `owner_user_id` | `owner_user_id INT NULL` |
| `active` | `active BOOLEAN DEFAULT TRUE` |
| `FOREIGN` | `FOREIGN KEY(category_id) REFERENCES categories(id)` |
| `FOREIGN` | `FOREIGN KEY(color_id) REFERENCES colors(id)` |
| `FOREIGN` | `FOREIGN KEY(style_id) REFERENCES styles(id)` |
| `FOREIGN` | `FOREIGN KEY(owner_user_id) REFERENCES users(id)` |

## wardrobe_items

| 컬럼/제약 | 실제 정의 |
|---|---|
| `id` | `id INT AUTO_INCREMENT PRIMARY KEY` |
| `user_id` | `user_id INT NOT NULL` |
| `item_id` | `item_id INT NOT NULL` |
| `UNIQUE` | `UNIQUE KEY uq_wardrobe(user_id,item_id)` |
| `FOREIGN` | `FOREIGN KEY(user_id) REFERENCES users(id)` |
| `FOREIGN` | `FOREIGN KEY(item_id) REFERENCES fashion_items(id)` |

## trends

| 컬럼/제약 | 실제 정의 |
|---|---|
| `id` | `id INT AUTO_INCREMENT PRIMARY KEY` |
| `year` | `year INT NOT NULL` |
| `season` | `season ENUM('봄','여름','가을','겨울') NOT NULL` |
| `style_id` | `style_id INT NOT NULL` |
| `score` | `score INT NOT NULL DEFAULT 50` |
| `notes` | `notes TEXT` |
| `FOREIGN` | `FOREIGN KEY(style_id) REFERENCES styles(id)` |

## outfits

| 컬럼/제약 | 실제 정의 |
|---|---|
| `id` | `id INT AUTO_INCREMENT PRIMARY KEY` |
| `user_id` | `user_id INT NULL` |
| `season` | `season VARCHAR(10) NOT NULL` |
| `style_id` | `style_id INT NOT NULL` |
| `total_price` | `total_price INT NOT NULL` |
| `balance_score` | `balance_score INT NOT NULL` |
| `created_at` | `created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP` |
| `FOREIGN` | `FOREIGN KEY(user_id) REFERENCES users(id)` |
| `FOREIGN` | `FOREIGN KEY(style_id) REFERENCES styles(id)` |

## outfit_items

| 컬럼/제약 | 실제 정의 |
|---|---|
| `outfit_id` | `outfit_id INT NOT NULL` |
| `item_id` | `item_id INT NOT NULL` |
| `PRIMARY` | `PRIMARY KEY(outfit_id,item_id)` |
| `FOREIGN` | `FOREIGN KEY(outfit_id) REFERENCES outfits(id)` |
| `FOREIGN` | `FOREIGN KEY(item_id) REFERENCES fashion_items(id)` |

## ratings

| 컬럼/제약 | 실제 정의 |
|---|---|
| `id` | `id INT AUTO_INCREMENT PRIMARY KEY` |
| `outfit_id` | `outfit_id INT NOT NULL` |
| `user_id` | `user_id INT NOT NULL` |
| `rating` | `rating INT NOT NULL CHECK(rating BETWEEN 1 AND 5)` |
| `FOREIGN` | `FOREIGN KEY(outfit_id) REFERENCES outfits(id)` |
| `FOREIGN` | `FOREIGN KEY(user_id) REFERENCES users(id)` |

## seasonal_looks

| 컬럼/제약 | 실제 정의 |
|---|---|
| `id` | `id INT AUTO_INCREMENT PRIMARY KEY` |
| `season` | `season ENUM('봄','여름','가을','겨울') NOT NULL` |
| `look_no` | `look_no TINYINT NOT NULL` |
| `title` | `title VARCHAR(100) NOT NULL` |
| `description` | `description VARCHAR(250)` |
| `image_url` | `image_url VARCHAR(255) NOT NULL` |
| `style_name` | `style_name VARCHAR(40) NOT NULL` |
| `sample_only` | `sample_only BOOLEAN NOT NULL DEFAULT TRUE` |
| `UNIQUE` | `UNIQUE KEY uq_season_look(season,look_no)` |

## style_profiles

| 컬럼/제약 | 실제 정의 |
|---|---|
| `user_id` | `user_id INT PRIMARY KEY` |
| `face_shape` | `face_shape ENUM('미선택','둥근형','타원형','각진형','긴형','하트형') NOT NULL DEFAULT '미선택'` |
| `body_shape` | `body_shape ENUM('미선택','직선형','상체강조형','하체강조형','허리강조형','균형형','슬림형','보통형','통통형') NOT NULL DEFAULT '미선택'` |
| `undertone` | `undertone ENUM('미선택','웜','쿨','뉴트럴') NOT NULL DEFAULT '미선택'` |
| `preferred_fit` | `preferred_fit ENUM('편안한핏','슬림핏','루즈핏') NOT NULL DEFAULT '편안한핏'` |
| `updated_at` | `updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP` |
| `FOREIGN` | `FOREIGN KEY (user_id) REFERENCES users(id)` |

## auth_links

| 컬럼/제약 | 실제 정의 |
|---|---|
| `token_hash` | `token_hash CHAR(64) PRIMARY KEY` |
| `email` | `email VARCHAR(255) NOT NULL` |
| `nickname` | `nickname VARCHAR(60) NOT NULL` |
| `expires_at` | `expires_at DATETIME NOT NULL` |
| `INDEX(email)` | `INDEX(email)` |

## auth_sessions

| 컬럼/제약 | 실제 정의 |
|---|---|
| `token_hash` | `token_hash CHAR(64) PRIMARY KEY` |
| `user_id` | `user_id INT NOT NULL` |
| `expires_at` | `expires_at DATETIME NOT NULL` |
| `FOREIGN` | `FOREIGN KEY(user_id) REFERENCES users(id)` |

## auth_limits

| 컬럼/제약 | 실제 정의 |
|---|---|
| `bucket` | `bucket CHAR(64) PRIMARY KEY` |
| `hits` | `hits INT NOT NULL DEFAULT 1` |
| `expires_at` | `expires_at DATETIME NOT NULL` |

## private_photos

| 컬럼/제약 | 실제 정의 |
|---|---|
| `filename` | `filename VARCHAR(80) PRIMARY KEY` |
| `user_id` | `user_id INT NOT NULL` |
| `FOREIGN` | `FOREIGN KEY(user_id) REFERENCES users(id)` |

## recommendation_history

| 컬럼/제약 | 실제 정의 |
|---|---|
| `id` | `id BIGINT AUTO_INCREMENT PRIMARY KEY` |
| `user_id` | `user_id INT NOT NULL` |
| `payload` | `payload JSON NOT NULL` |
| `created_at` | `created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP` |
| `FOREIGN` | `FOREIGN KEY(user_id) REFERENCES users(id)` |
| `INDEX(user_id,created_at)` | `INDEX(user_id,created_at)` |

## 데이터 귀속·보호

users.id가 개인 자료의 기준 PK입니다. wardrobe_items·style_profiles·private_photos·recommendation_history·auth_sessions는 user_id로 연결합니다. fashion_items.owner_user_id NULL은 공용, 값이 있으면 개인 상품입니다. QR에는 가입 URL만 담고 인증 토큰은 별도 일회용 링크로 발급합니다. auth_links/auth_sessions의 PK는 토큰 원문이 아닌 SHA-256 해시입니다.

개인 사진 파일과 MySQL은 함께 백업합니다. 사진 경로만 백업해 실제 파일이 빠지거나 DB만 복구하면 이미지가 복구되지 않습니다. 가격 INT는 원화 추가 구매 비용이고 외화 환율 변환은 구현하지 않았습니다.
