CREATE DATABASE iot CHARACTER SET utf8 COLLATE utf8_general_ci;
USE iot;
CREATE USER 'user'@'localhost' IDENTIFIED BY 'asdf1234';
GRANT ALL ON *.* to 'user'@'localhost';

CREATE TABLE log_t(
log_id INT AUTO_INCREMENT,
log_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
log_text varchar(300),
log_color int,
PRIMARY KEY (log_id)
);

INSERT INTO log_t(log_text) VALUES ("ログ用データベースを作成しました");