CREATE TABLE `follows` (
  `following_user_id` bigint,
  `followed_user_id` bigint,
  `created_at` timestamp NOT NULL DEFAULT (now()),
  CONSTRAINT `user cannot follow self` CHECK (following_user_id != followed_user_id),
  PRIMARY KEY (`following_user_id`, `followed_user_id`)
);

CREATE TABLE `favorites` (
  `listing_id` bigint,
  `user_id` bigint,
  `created_at` timestamp NOT NULL DEFAULT (now()),
  PRIMARY KEY (`user_id`, `listing_id`)
);

CREATE TABLE `user` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `email` varchar(255) UNIQUE NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `username` varchar(255) UNIQUE NOT NULL,
  `phone` varchar(40),
  `created_at` timestamp NOT NULL DEFAULT (now()),
  `updated_at` timestamp NOT NULL DEFAULT (now())
);

CREATE TABLE `status` (
  `id` bigint PRIMARY KEY,
  `name` varchar(20)
);

CREATE TABLE `currency` (
  `code` char(3) PRIMARY KEY,
  `name` varchar(100) NOT NULL,
  `symbol` varchar(8) NOT NULL,
  `decimal_places` smallint NOT NULL
);

CREATE TABLE `listing` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `scientific_name` varchar(255),
  `quantity` integer NOT NULL CHECK (quantity >= 0),
  `price_perunit` decimal(19,4) NOT NULL CHECK (price_perunit >= 0),
  `currency_code` char(3) NOT NULL,
  `address_line_1` varchar(255),
  `address_line_2` varchar(255),
  `suburb` varchar(100),
  `state` varchar(100),
  `postal_code` varchar(20),
  `country_code` char(2),
  `description` text,
  `seller_user_id` bigint NOT NULL,
  `status` bigint NOT NULL DEFAULT 0,
  `created_at` timestamp NOT NULL DEFAULT (now()),
  `updated_at` timestamp NOT NULL DEFAULT (now())
);

ALTER TABLE `favorites` ADD FOREIGN KEY (`user_id`) REFERENCES `user` (`id`);

ALTER TABLE `favorites` ADD FOREIGN KEY (`listing_id`) REFERENCES `listing` (`id`);

ALTER TABLE `listing` ADD FOREIGN KEY (`status`) REFERENCES `status` (`id`);

ALTER TABLE `listing` ADD FOREIGN KEY (`currency_code`) REFERENCES `currency` (`code`);

ALTER TABLE `listing` ADD FOREIGN KEY (`seller_user_id`) REFERENCES `user` (`id`);

ALTER TABLE `follows` ADD FOREIGN KEY (`following_user_id`) REFERENCES `user` (`id`);

ALTER TABLE `follows` ADD FOREIGN KEY (`followed_user_id`) REFERENCES `user` (`id`);

-- Disable foreign key checks for INSERT
SET FOREIGN_KEY_CHECKS = 0;

INSERT INTO `status` (`id`, `name`)
VALUES
  (0, 'AVAILABLE'),
  (1, 'SOLDOUT'),
  (2, 'PENDING');
INSERT INTO `currency` (`code`, `name`, `symbol`, `decimal_places`)
VALUES
  ('AUD', 'Australia', '$', 2);

-- Re-enable foreign key checks
SET FOREIGN_KEY_CHECKS = 1;