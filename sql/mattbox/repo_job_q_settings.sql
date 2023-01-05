CREATE TABLE `repo_job_q_settings` (
  `max_jobs` int(11) NOT NULL,
  `min_jobs` int(11) NOT NULL,
  `sleep_time_if_empty_seconds` int(11) DEFAULT NULL,
  `last_batch_size_added` int(11) NOT NULL,
  `last_batch_tstamp` datetime DEFAULT NULL,
  `delay_expiration` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4