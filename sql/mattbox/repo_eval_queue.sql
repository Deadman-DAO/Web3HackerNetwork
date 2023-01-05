CREATE TABLE `repo_eval_queue` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `owner` varchar(128) NOT NULL,
  `name` varchar(128) NOT NULL,
  `watchers` int(11) DEFAULT 0,
  `repo_size` int(11) DEFAULT 0,
  `subscribers` int(11) DEFAULT 0,
  `inserted_at` datetime DEFAULT NULL,
  `xfer` tinyint(1) DEFAULT 0,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=283128 DEFAULT CHARSET=utf8mb4