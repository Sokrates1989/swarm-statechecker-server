CREATE TABLE `state_checker`.`checked_tools` 
(
	`ID` BIGINT NOT NULL AUTO_INCREMENT , 
	`name` TEXT NOT NULL , 
	`description` TEXT NOT NULL , 
	`token` TEXT NOT NULL , 
	`stateCheckFrequency_inMinutes` INT NOT NULL , 
	`lastTimeToolWasUp` BIGINT NOT NULL ,
	`toolIsDownMessageHasBeenSent` TINYINT NOT NULL DEFAULT '0',

	PRIMARY KEY (`ID`)
) ENGINE = InnoDB;