select age(t_finished,t_started) from jobs where t_created > '2016-01-04'::date and t_started is not null and t_finished is not null;
select avg(t_finished-t_started) from jobs where t_created > '2016-01-04'::date and t_started is not null and t_finished is not null
