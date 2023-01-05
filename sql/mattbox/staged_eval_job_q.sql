CREATE TABLE `staged_eval_job_q` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `repo_id` int(11) NOT NULL,
  `tstamp` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `repo_id` (`repo_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3274611 DEFAULT CHARSET=utf8mb4