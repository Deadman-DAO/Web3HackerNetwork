CREATE TABLE `hacker_import_association` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `alias_id` int(11) NOT NULL,
  `import_id` int(11) NOT NULL,
  `count` float NOT NULL DEFAULT 0,
  `tstamp` datetime(3) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `hacker_import_composite` (`alias_id`,`import_id`)
) ENGINE=InnoDB AUTO_INCREMENT=10213248 DEFAULT CHARSET=utf8mb4