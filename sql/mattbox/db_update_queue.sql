CREATE TABLE `db_update_queue` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tstamp` datetime DEFAULT NULL,
  `machine_name` varchar(64) DEFAULT NULL,
  `repo_owner` varchar(128) DEFAULT NULL,
  `repo_name` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=832 DEFAULT CHARSET=utf8mb4