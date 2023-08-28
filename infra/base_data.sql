insert into categories (category_name) 
values ('sushi-rolls'), 
	   ('sushi-set');
insert into products (product_name, category_id, price) 
values ('Philadelphia with Salmon',	1, 320.00), 
	   ('Philadelphia with Tuna', 1, 300.0),
	   ('Philadelphia with Shrimp', 1, 310.0);
insert into users (username, user_password, role_id, is_active) 
values ('artem', '$2b$12$ym5CRNR39iSptUcdzpFKQO2.yvB.DstG.4QCHr5WPIIW2KL/vafIy', 1, true), -- password 123
	   ('customer_1', '$2b$12$ym5CRNR39iSptUcdzpFKQO2.yvB.DstG.4QCHr5WPIIW2KL/vafIy', 3, true); -- password 123
