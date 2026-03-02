aws_region   = "us-east-1"
project_name = "k8s-mcp"
environment  = "dev"

vpc_cidr             = "10.0.0.0/16"
public_subnet_cidrs  = ["10.0.1.0/24", "10.0.2.0/24"]
private_subnet_cidrs = ["10.0.11.0/24", "10.0.12.0/24"]

eks_cluster_version = "1.34"
node_desired_size   = 2
node_min_size       = 1
node_max_size       = 5
node_instance_type  = "t3.medium"
node_disk_size      = 20

bastion_instance_type = "t3.medium"
key_name              = "dev-mcp"
allowed_cidr_blocks   = ["0.0.0.0/0"]
