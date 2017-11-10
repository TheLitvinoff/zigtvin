CREATE TABLE `schedule`.`section` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` char(25) DEFAULT NULL,
  PRIMARY KEY (`id`)
);

ALTER TABLE `schedule`.`activity`
ADD section_id INT;

ALTER TABLE `schedule`.`activity`
ADD FOREIGN KEY (section_id) references section(id); 

ALTER TABLE `schedule`.`section`
ADD user_id INT;

ALTER TABLE `schedule`.`section`
ADD FOREIGN KEY (user_id) references users(id);