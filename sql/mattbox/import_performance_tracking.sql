CREATE TABLE `import_performance_tracking` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `repo_id` int(11) DEFAULT NULL,
  `success` bit(1) DEFAULT NULL,
  `stats_json` longblob DEFAULT NULL,
  `starttime` datetime DEFAULT NULL,
  `endtime` datetime DEFAULT NULL,
  `hacker_name_map_size` int(11) DEFAULT NULL,
  `hacker_name_map_completion` datetime DEFAULT NULL,
  `extension_map_size` int(11) DEFAULT NULL,
  `extension_map_completion` datetime DEFAULT NULL,
  `import_map_map_size` int(11) DEFAULT NULL,
  `import_map_map_completion` datetime DEFAULT NULL,
  `hacker_extension_map_size` int(11) DEFAULT NULL,
  `hacker_extension_map_completion` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `repo_id` (`repo_id`),
  CONSTRAINT `import_performance_tracking_ibfk_1` FOREIGN KEY (`repo_id`) REFERENCES `repo` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=252277 DEFAULT CHARSET=utf8mb4