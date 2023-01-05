CREATE TABLE `commit_stats` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `commit_id` int(11) NOT NULL,
  `file_type` varchar(128) DEFAULT NULL,
  `insert_count` int(11) DEFAULT NULL,
  `delete_count` int(11) DEFAULT NULL,
  `occurrence_count` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `commit_stats_Idx` (`id`),
  KEY `xelda` (`commit_id`),
  KEY `commit_stats_fileType_idx` (`file_type`),
  CONSTRAINT `xelda` FOREIGN KEY (`commit_id`) REFERENCES `commit` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4516001 DEFAULT CHARSET=utf8mb4