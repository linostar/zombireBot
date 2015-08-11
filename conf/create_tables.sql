-- Database `zombiredb`

-- Table structure for table `users`

CREATE TABLE IF NOT EXISTS `users` (
  `userid` int NOT NULL AUTO_INCREMENT,
  `nick` varchar(64) NOT NULL,
  `main_nick` varchar(64) NOT NULL,
  `type` varchar(1) NOT NULL,
  `hp` int NOT NULL DEFAULT 10,
  `mmp` smallint NOT NULL DEFAULT 5,
  `score` int NOT NULL DEFAULT 0,
  `bonus` smallint NOT NULL DEFAULT 0,
  PRIMARY KEY(`userid`)
) ENGINE=MyISAM	DEFAULT CHARSET=utf8;

-- Table structure for table `profiles`

CREATE TABLE IF NOT EXISTS `profiles` (
  `prid` int NOT NULL AUTO_INCREMENT,
  `nick` varchar(64) NOT NULL,
  `autovals` smallint NOT NULL DEFAULT 0,
  `extras` int NOT NULL DEFAULT 0,
  PRIMARY KEY(`prid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- Table structure for table `arsenal`

CREATE TABLE IF NOT EXISTS `arsenals` (
  `aid` int NOT NULL AUTO_INCREMENT,
  `nick` varchar(64) NOT NULL,
  `sword` smallint NOT NULL DEFAULT 0,
  `slife` smallint NOT NULL DEFAULT 0,
  `armor` smallint NOT NULL DEFAULT 0,
  `alife` smallint NOT NULL DEFAULT 0,
  PRIMARY KEY(`aid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- Table structure for table `highscores`

CREATE TABLE IF NOT EXISTS `highscores` (
  `hsid` int NOT NULL AUTO_INCREMENT,
  `nick` varchar(64) NOT NULL,
  `type` varchar(1) NOT NULL,
  `score` int NOT NULL DEFAULT 0,
  `date` varchar(12) NOT NULL,
  PRIMARY KEY(`hsid`)
) ENGINE=MyISAM	DEFAULT CHARSET=utf8;
