CREATE TABLE `commit` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `commit_id` char(40) NOT NULL,
  `alias_id` int(11) NOT NULL,
  `date` datetime DEFAULT NULL,
  `gmt_offset` varchar(16) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `commitIdIdx` (`commit_id`),
  KEY `wtf` (`alias_id`),
  KEY `idx` (`id`),
  CONSTRAINT `wtf` FOREIGN KEY (`alias_id`) REFERENCES `alias` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=17574970 DEFAULT CHARSET=utf8mb4