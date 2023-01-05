CREATE TABLE `rediculous_fucking_work_around` (
  `connection_id` int(11) NOT NULL,
  `repo_id` int(11) NOT NULL,
  `transaction_id` int(11) DEFAULT NULL,
  `tstamp` datetime DEFAULT NULL,
  PRIMARY KEY (`connection_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4