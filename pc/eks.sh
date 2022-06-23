# access keys
aws iam list-access-keys
aws iam delete-access-key --access-key-id <>
aws iam create-access-key
# delete eks cluster
aws eks list-clusters
aws eks list-nodegroups --cluster-name <>
aws eks delete-nodegroup --cluster-name <> --nodegroup-name <>
aws eks delete-cluster --name <>
#delete vpc
aws ec2 describe-subnets
aws ec2 delete-subnet --subnet-id <>
aws ec2 describe-vpc-peering-connections --filters 'Name=requester-vpc-info.vpc-id,Values='$vpc | grep VpcPeeringConnectionId
aws ec2 describe-nat-gateways --filter 'Name=vpc-id,Values='$vpc | grep NatGatewayId
aws ec2 delete-nat-gateway --nat-gateway-id <>
aws ec2 describe-instances  --filters 'Name=vpc-id,Values='$vpc | grep InstanceId
aws ec2 describe-vpn-gateways --filters 'Name=attachment.vpc-id,Values='$vpc | grep VpnGatewayId
