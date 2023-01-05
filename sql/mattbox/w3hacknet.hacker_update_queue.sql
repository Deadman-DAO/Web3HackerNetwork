CREATE TABLE `hacker_update_queue` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `md5` char(32) DEFAULT NULL,
  `name_email` varchar(256) DEFAULT NULL,
  `commit_count` int(11) DEFAULT NULL,
  `min_date` datetime DEFAULT NULL,
  `max_date` datetime DEFAULT NULL,
  `repo_owner` varchar(128) DEFAULT NULL,
  `repo_name` varchar(128) DEFAULT NULL,
  `commit_array` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`commit_array`)),
  `file_extension` varchar(64) DEFAULT NULL,
  `file_extension_count` int(11) DEFAULT NULL,
  `import_lang_ext` varchar(64) DEFAULT NULL,
  `import_name` varchar(256) DEFAULT NULL,
  `import_contributions` double DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5712 DEFAULT CHARSET=utf8mb4