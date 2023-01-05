CREATE TABLE `alias` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `md5` char(32) NOT NULL,
  `name` varchar(256) DEFAULT NULL,
  `count` int(11) DEFAULT 0,
  `github_user_id` varchar(64) DEFAULT NULL,
  `last_traced` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `aliasIdx` (`md5`),
  KEY `alias_github_user_id_IDX` (`github_user_id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=3417519 DEFAULT CHARSET=utf8mb4