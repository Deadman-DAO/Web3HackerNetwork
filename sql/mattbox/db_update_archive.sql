CREATE TABLE `db_update_archive` (
  `db_update_queue_id` int(11) NOT NULL,
  `reserved` datetime DEFAULT NULL,
  `completed` datetime DEFAULT NULL,
  PRIMARY KEY (`db_update_queue_id`),
  UNIQUE KEY `db_update_queue_id` (`db_update_queue_id`),
  CONSTRAINT `dua_c` FOREIGN KEY (`db_update_queue_id`) REFERENCES `db_update_queue` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4