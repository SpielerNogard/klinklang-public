CREATE TABLE IF NOT EXISTS `codes` (
	`email` VARCHAR(255),
	`code` VARCHAR(255),
	`updated` TIMESTAMP,
	PRIMARY KEY (`email`)
);