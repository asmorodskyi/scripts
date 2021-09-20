select flavor, AVG(t_started-t_created) from jobs where flavor in ('AZURE-Standard-Updates', 'EC2-ARM-Updates', 'AZURE-Basic-Image-Updates', 'EC2-Updates', 'AZURE-Standard-gen2-Updates', 'AZURE-BYOS-gen2-Updates', 'AZURE-Priority-Updates', 'GCE-Updates', 'EC2-BYOS-Updates', 'EC2-BYOS-ARM-Updates', 'EC2-BYOS-ARM-Updates', 'GCE-BYOS-Updates', 'AZURE-BYOS-Updates', 'AZURE-Basic-gen2-Updates') and state = 'done' and test in ('publiccloud_boottime', 'publiccloud_upload_img', 'mau-extratests-publiccloud', 'publiccloud_ltp_cve', 'qem_publiccloud_img_proof', 'publiccloud_img_proof', 'mau-extratests-docker-publiccloud', 'publiccloud_ltp_syscalls', 'publiccloud_download_testrepos') and t_created > '2021-04-26'::date group by flavor order by 2;
select flavor, AVG(t_finished-t_started) from jobs where flavor in ('AZURE-Standard-Updates', 'EC2-ARM-Updates', 'AZURE-Basic-Image-Updates', 'EC2-Updates', 'AZURE-Standard-gen2-Updates', 'AZURE-BYOS-gen2-Updates', 'AZURE-Priority-Updates', 'GCE-Updates', 'EC2-BYOS-Updates', 'EC2-BYOS-ARM-Updates', 'EC2-BYOS-ARM-Updates', 'GCE-BYOS-Updates', 'AZURE-BYOS-Updates', 'AZURE-Basic-gen2-Updates') and state = 'done' and test in ('publiccloud_boottime', 'publiccloud_upload_img', 'mau-extratests-publiccloud', 'publiccloud_ltp_cve', 'qem_publiccloud_img_proof', 'publiccloud_img_proof', 'mau-extratests-docker-publiccloud', 'publiccloud_ltp_syscalls', 'publiccloud_download_testrepos') and t_created > '2021-04-26'::date group by flavor order by 2;
select version, flavor, AVG(t_started-t_created) from jobs where test='mau-extratests-publiccloud' and state = 'done' group by version,flavor order by 3;