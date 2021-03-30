CREATE DATABASE `test_database`;

CREATE TABLE `stocks` (
  `id` int NOT NULL AUTO_INCREMENT,
  `sku` varchar(10) NOT NULL,
  `qty` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `stocks_sku_IDX` (`sku`)
) ENGINE=InnoDB ;


CREATE TABLE `reserves` (
  `id` int NOT NULL AUTO_INCREMENT,
  `sku` varchar(10) NOT NULL,
  `qty` int NOT NULL DEFAULT '0',
  `status` varchar(10) NOT NULL DEFAULT 'pre',
  `batch` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `reserves_sku_IDX` (`sku`,`status`),
  KEY `reserves_batch_IDX` (`batch`)
) ENGINE=InnoDB;