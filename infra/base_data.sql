insert into categories (category_id, category_name)
values ('d70688fe-7b1d-435a-9c9a-b5ed38bd22cc', 'sushi-rolls'),
	   ('8eb0a7fc-3f8f-42fa-98da-9b311b6d86a3', 'sushi-set');

insert into products (product_id, product_name, category_id, price)
values ('ce69cbac-3fe4-4e9c-b9c7-d9f148f4c4f9', 'Philadelphia with Salmon',	'd70688fe-7b1d-435a-9c9a-b5ed38bd22cc', 320.00),
	   ('09b87ca7-701b-4c83-aedb-51b69effc5d1', 'Philadelphia with Tuna', 'd70688fe-7b1d-435a-9c9a-b5ed38bd22cc', 300.0),
	   ('a7201f73-7127-4ea5-a8f1-c888069bbb9e', 'Philadelphia with Shrimp', 'd70688fe-7b1d-435a-9c9a-b5ed38bd22cc', 310.0);

insert into users (user_id, username, user_password, role_id, is_active)
values ('d91e29d1-5019-471b-ad69-b7f8641cef59', 'artem', '$2b$12$ym5CRNR39iSptUcdzpFKQO2.yvB.DstG.4QCHr5WPIIW2KL/vafIy', 1, true), -- password 123
	   ('b2dd8336-cc9c-457a-aa4f-f0be05a0ad96', 'customer_1', '$2b$12$ym5CRNR39iSptUcdzpFKQO2.yvB.DstG.4QCHr5WPIIW2KL/vafIy', 3, true); -- password 123