-- Database `zombiredb`
-- Table structure for table `users`

CREATE TABLE IF NOT EXISTS `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nick` varchar(64) NOT NULL,
  `main_nick` varchar(64) NOT NULL,
  `type` varchar(1) NOT NULL,
  `points` int NOT NULL DEFAULT 0,
  PRIMARY KEY(`id`)
) ENGINE=MyISAM	DEFAULT CHARSET=utf8;
