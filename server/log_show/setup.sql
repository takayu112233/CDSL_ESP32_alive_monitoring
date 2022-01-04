CREATE DATABASE iot CHARACTER SET utf8 COLLATE utf8_general_ci;
USE iot;
CREATE USER 'user'@'localhost';
GRANT ALL ON *.* to 'user'@'localhost';
SET PASSWORD FOR 'user'@'localhost' = PASSWORD('asdf1234');

CREATE TABLE log_t(
log_id INT AUTO_INCREMENT,
log_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
log_text varchar(300),
log_color int,
PRIMARY KEY (log_id)
);

INSERT INTO log_t(log_text) VALUES ("ログ用データベースを作成しました");