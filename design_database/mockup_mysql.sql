CREATE TABLE `follows` (
  `following_user_id` bigint,
  `followed_user_id` bigint,
  `created_at` timestamp NOT NULL,
  PRIMARY KEY (`following_user_id`, `followed_user_id`)
);

CREATE TABLE `favorites` (
  `listings_id` bigint,
  `user_id` bigint,
  `created_at` timestamp NOT NULL,
  PRIMARY KEY (`user_id`, `listings_id`)
);

CREATE TABLE `users` (
  `id` bigint PRIMARY KEY,
  `username` varchar(255) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `created_at` timestamp NOT NULL,
  `updated_at` timestamp NOT NULL
);

CREATE TABLE `listings` (
  `id` bigint PRIMARY KEY,
  `name` varchar(255) NOT NULL,
  `scientific_name` varchar(255),
  `quantity` integer NOT NULL,
  `address_line_1` varchar(255),
  `address_line_2` varchar(255),
  `suburb` varchar(100),
  `state` varchar(100),
  `postal_code` varchar(20),
  `country_code` varchar(2),
  `description` text,
  `user_id` bigint NOT NULL,
  `status` varchar(20) NOT NULL,
  `created_at` timestamp NOT NULL,
  `updated_at` timestamp NOT NULL
);

ALTER TABLE `favorites` ADD FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

ALTER TABLE `favorites` ADD FOREIGN KEY (`listings_id`) REFERENCES `listings` (`id`);

ALTER TABLE `listings` ADD FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

ALTER TABLE `follows` ADD FOREIGN KEY (`following_user_id`) REFERENCES `users` (`id`);

ALTER TABLE `follows` ADD FOREIGN KEY (`followed_user_id`) REFERENCES `users` (`id`);
