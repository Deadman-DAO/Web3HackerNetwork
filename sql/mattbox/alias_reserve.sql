CREATE TABLE `alias_reserve` (
  `alias_id` int(11) NOT NULL,
  `tstamp` datetime DEFAULT NULL,
  `reserver` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`alias_id`),
  UNIQUE KEY `alias_id` (`alias_id`),
  CONSTRAINT `no_dups` FOREIGN KEY (`alias_id`) REFERENCES `alias` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4