CREATE TABLE `repos_staged_for_eval_reserve` (
  `repo_id` int(11) DEFAULT NULL,
  `machine` varchar(64) DEFAULT NULL,
  UNIQUE KEY `repo_id` (`repo_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4