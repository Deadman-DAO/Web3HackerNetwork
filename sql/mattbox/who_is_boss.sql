CREATE TABLE `who_is_boss` (
  `task_name` varchar(32) DEFAULT NULL,
  `expiration_date` datetime NOT NULL,
  `unique_id` char(32) DEFAULT NULL,
  UNIQUE KEY `task_name` (`task_name`),
  UNIQUE KEY `unique_id` (`unique_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4