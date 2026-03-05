select * from workers where id in ( select assigned_worker_id from jobs where result='incomplete' and t_created > '2026-02-09'::date);
