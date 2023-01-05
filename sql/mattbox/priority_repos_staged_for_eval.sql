CREATE TABLE `priority_repos_staged_for_eval` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `repo_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `repo_id` (`repo_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4