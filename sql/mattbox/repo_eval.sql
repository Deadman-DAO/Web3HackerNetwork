CREATE TABLE `repo_eval` (
  `repo_id` int(11) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `pushed_at` datetime DEFAULT NULL,
  `homepage` varchar(128) DEFAULT NULL,
  `size` int(11) DEFAULT NULL,
  `watchers` int(11) DEFAULT NULL,
  `contributor_count` int(11) DEFAULT NULL,
  `contributor_sum` int(11) DEFAULT NULL,
  `commit_count_last_year` int(11) DEFAULT NULL,
  `parallel_repo_count` int(11) DEFAULT NULL,
  `subscribers` int(11) DEFAULT -1,
  PRIMARY KEY (`repo_id`),
  UNIQUE KEY `repo_id` (`repo_id`),
  CONSTRAINT `repo_eval_ibfk_1` FOREIGN KEY (`repo_id`) REFERENCES `repo` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4