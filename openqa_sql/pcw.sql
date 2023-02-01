select distinct type from ocw_cspinfo where instance_id in (select id from ocw_instance where provider='GCE');
select distinct type from ocw_cspinfo where instance_id in (select id from ocw_instance where provider='AZURE');
select distinct type from ocw_cspinfo where instance_id in (select id from ocw_instance where provider='EC2');
select type, count(*) from ocw_cspinfo where instance_id in (select id from ocw_instance where provider='EC2' and first_seen > date('now','-1 month') ) group by type;
select type, count(*) from ocw_cspinfo where instance_id in (select id from ocw_instance where provider='EC2' and first_seen > date('now','-1 month') and vault_namespace='ccoe' ) group by type order by 2;
