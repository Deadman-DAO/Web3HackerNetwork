-- w3hacknet.repo_commit definition
use w3hacknet;
drop table repo_commit;
CREATE TABLE `repo_commit` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `commit_id` int(11) NOT NULL,
  `repo_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `weird` (`commit_id`),
  KEY `weirder` (`repo_id`),
  CONSTRAINT `weird` FOREIGN KEY (`commit_id`) REFERENCES `commit` (`id`),
  CONSTRAINT `weirder` FOREIGN KEY (`repo_id`) REFERENCES `repo` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4;