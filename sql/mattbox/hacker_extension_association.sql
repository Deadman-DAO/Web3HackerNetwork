CREATE TABLE `hacker_extension_association` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `alias_id` int(11) NOT NULL,
  `extension_id` int(11) NOT NULL,
  `count` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  UNIQUE KEY `alias_extension_composite` (`alias_id`,`extension_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2366218 DEFAULT CHARSET=utf8mb4