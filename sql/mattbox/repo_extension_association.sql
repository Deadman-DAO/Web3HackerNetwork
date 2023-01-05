CREATE TABLE `repo_extension_association` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `repo_id` int(11) NOT NULL,
  `extension_id` int(11) NOT NULL,
  `count` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  UNIQUE KEY `repo_extension_composite` (`repo_id`,`extension_id`)
) ENGINE=InnoDB AUTO_INCREMENT=458404 DEFAULT CHARSET=utf8mb4