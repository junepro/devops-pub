data "aws_ec2_instance_type_offerings" "my_ins_type1"{
  filter {
    name   = "instance-type"
    values = ["t2.micro"]
  }
  filter {
    name   = "location"
    values = ["us-east-1a"]
  }
  location_type = "availability-zone"
}

output "ouput_v1_1" {
  value = data.aws_ec2_instance_type_offerings.my_ins_type1.instance_types
}