CREATE TABLE IF NOT EXISTS `schema_migrations` (
    `id` BIGINT NOT NULL AUTO_INCREMENT,
    `migration` VARCHAR(255) NOT NULL,
    `applied_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB;