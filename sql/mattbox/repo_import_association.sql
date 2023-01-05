CREATE TABLE `repo_import_association` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `repo_id` int(11) NOT NULL,
  `import_id` int(11) NOT NULL,
  `count` float DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `repo_import_composite` (`repo_id`,`import_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3152540 DEFAULT CHARSET=utf8mb4