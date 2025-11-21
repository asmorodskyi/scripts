select test,distri,version,flavor,arch,build,machine from jobs where id in (select job_id from job_settings where key='PARALLEL_WITH' and value='hacluster-supportserver') order by 2;
select id,t_started,t_finished,result,state from jobs where t_created > current_date - 1  and test='hacluster-supportserver' order by 1,2;
select distinct(test),result, first_value(id) OVER ( partition by test order by test, t_created) from jobs where id in (select job_id from job_modules where t_created > '2017-02-01'::date and script='tests/support_server/boot.pm');
select test,distri,version,flavor,arch,build,machine,assigned_worker_id from jobs where id in (select job_id from job_modules where t_created > '2017-05-04'::date and script='tests/installation/bootloader_uefi.pm') and build='0367';
select job_id from job_modules where id in (select 17781100 from needles where filename='installation-autoyast-error-20160505.json');
select test,distri,version,flavor,arch,build,machine from jobs where id in (select job_id  from job_modules where result='failed' and script='tests/x11/reboot_gnome.pm');


#for cascade delete

select * from jobs where test='hpc_install' and flavor='Server-DVD';
select * from job_modules where job_id in (select id from jobs where test='hpc_install' and flavor='Server-DVD');


select count(j.id),date_trunc('day', j.t_created) AS day from jobs j join job_settings js on j.id = js.job_id where j.t_created >= '2025-07-12' and js.key = 'WORKER_CLASS' and js.value in ('pc_azure_qac', 'pc_ec2_qac', 'pc_gce_qac') group by day;
