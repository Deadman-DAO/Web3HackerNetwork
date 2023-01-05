CREATE TABLE `file_extension` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ext` varchar(64) NOT NULL,
  `description` varchar(256) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ext_idx` (`ext`)
) ENGINE=InnoDB AUTO_INCREMENT=45143 DEFAULT CHARSET=utf8mb4