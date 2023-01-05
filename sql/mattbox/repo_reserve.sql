CREATE TABLE `repo_reserve` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `repo_id` int(11) NOT NULL,
  `tstamp` datetime DEFAULT NULL,
  `reserver` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `repo_id` (`repo_id`),
  CONSTRAINT `repo_reserve_ibfk_1` FOREIGN KEY (`repo_id`) REFERENCES `repo` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1236463 DEFAULT CHARSET=utf8mb4