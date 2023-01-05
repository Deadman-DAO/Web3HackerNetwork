CREATE TABLE `source_import` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(256) NOT NULL,
  `extension_id` int(11) NOT NULL,
  `parent_import` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=294975 DEFAULT CHARSET=utf8mb4