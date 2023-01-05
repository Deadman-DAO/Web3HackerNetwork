CREATE TABLE `repo_job_q_filler_reservation` (
  `singleton` int(11) NOT NULL DEFAULT 666,
  `tstamp` datetime NOT NULL,
  `ewenique` int(11) NOT NULL,
  UNIQUE KEY `q_key` (`singleton`,`tstamp`,`ewenique`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4