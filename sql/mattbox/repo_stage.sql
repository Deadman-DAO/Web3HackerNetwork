CREATE TABLE `repo_stage` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `repo_owner` varchar(128) DEFAULT NULL,
  `repo_name` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `stage_idx` (`repo_owner`,`repo_name`)
) ENGINE=InnoDB AUTO_INCREMENT=8104 DEFAULT CHARSET=utf8mb4