#!/usr/bin/perl
use YAML::PP;

my $ypp     = YAML::PP->new(header => 0, schema => [qw/ + Merge /]);
my $content = $ypp->load_file('/home/asmorodskyi/source/qac-openqa-yaml/publiccloud/updates/12sp4.yaml');
$content->{defaults} = 'sssss';
$ypp->dump_file('/home/asmorodskyi/source/qac-openqa-yaml/publiccloud/updates/12sp4.yaml',$content);
