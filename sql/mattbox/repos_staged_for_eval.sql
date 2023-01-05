CREATE TABLE `repos_staged_for_eval` (
  `repo_id` int(11) DEFAULT NULL,
  `owner` varchar(128) DEFAULT NULL,
  `name` varchar(128) DEFAULT NULL,
  `randy` float DEFAULT NULL,
  `reserved_by` varchar(64) DEFAULT NULL,
  `priority` int(11) DEFAULT 0,
  UNIQUE KEY `uix2` (`repo_id`),
  KEY `uix` (`randy`,`repo_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4