use clawer;

update auth_user set is_superuser = 1;
update auth_user set is_staff = 1;
insert into django_site (`domain`, `name`) values ('http://www.baidu.com', "baidu");

