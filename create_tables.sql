-- Database `zombiredb`

-- Table structure for table `users`

CREATE TABLE IF NOT EXISTS `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nick` varchar(64) NOT NULL,
  `main_nick` varchar(64) NOT NULL,
  `type` varchar(1) NOT NULL,
  `points` int NOT NULL DEFAULT 0,
  `max_power` smallint NOT NULL DEFAULT 3,
  `bonus` smallint NOT NULL DEFAULT 0,
  PRIMARY KEY(`id`)
) ENGINE=MyISAM	DEFAULT CHARSET=utf8;

-- Table structure for table `highscores`

CREATE TABLE IF NOT EXISTS `highscores` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nick` varchar(64) NOT NULL,
  `type` varchar(1) NOT NULL,
  `score` int NOT NULL DEFAULT 0,
  `date` varchar(12) NOT NULL,
  PRIMARY KEY(`id`)
) ENGINE=MyISAM	DEFAULT CHARSET=utf8;
