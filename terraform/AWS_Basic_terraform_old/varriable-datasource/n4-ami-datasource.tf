data "aws_ami" "amzlinux2" {
  most_recent      = true
  owners           = ["amazon"]
  filter {
    name   = "name"
    values = ["myami-*"]
  }
  filter {
    name   = "root-device-type"
    values = ["ebs"]
  }
  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
  filter {
    name   = "architecture"
    values = ["x84_64"]
  }
}