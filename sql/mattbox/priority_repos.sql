CREATE TABLE `priority_repos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `repo_owner` varchar(128) DEFAULT NULL,
  `repo_name` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `combo` (`repo_owner`,`repo_name`)
) ENGINE=InnoDB AUTO_INCREMENT=2493 DEFAULT CHARSET=utf8mb4