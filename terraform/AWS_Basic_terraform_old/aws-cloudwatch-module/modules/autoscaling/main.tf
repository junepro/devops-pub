resource "aws_launch_template" "my_launch_template" {
  name          = "my-launch-template"
  description   = "My Launch template"
  image_id      = var.ami_id
  instance_type = var.instance_type

  vpc_security_group_ids = [var.private_sg_id]
  key_name               = var.instance_keypair
  user_data              = var.launch_template_user_data_base64
  ebs_optimized          = true
  update_default_version = true

  block_device_mappings {
    device_name = "/dev/sda1"
    ebs {
      volume_size           = 20
      delete_on_termination = true
      volume_type           = "gp2"
    }
  }

  monitoring {
    enabled = true
  }

  tag_specifications {
    resource_type = "instance"
    tags = {
      Name = "myasg"
    }
  }
}

resource "aws_autoscaling_group" "my_asg" {
  name_prefix         = "myasg-"
  desired_capacity    = 2
  max_size            = 10
  min_size            = 2
  vpc_zone_identifier = var.private_subnet_ids
  target_group_arns   = [var.target_group_arn]
  health_check_type   = "EC2"

  launch_template {
    id      = aws_launch_template.my_launch_template.id
    version = aws_launch_template.my_launch_template.latest_version
  }

  instance_refresh {
    strategy = "Rolling"
    preferences {
      min_healthy_percentage = 50
    }
    triggers = ["desired_capacity"]
  }

  tag {
    key                 = "Owners"
    value               = "Web-Team"
    propagate_at_launch = true
  }
}

# SNS Topic for notifications
resource "aws_sns_topic" "myasg_sns_topic" {
  name = "myasg-sns-topic-${var.sns_topic_suffix}"
}

resource "aws_sns_topic_subscription" "myasg_sns_topic_subscription" {
  topic_arn = aws_sns_topic.myasg_sns_topic.arn
  protocol  = "email"
  endpoint  = var.sns_notification_email
}

resource "aws_autoscaling_notification" "myasg_notifications" {
  group_names = [aws_autoscaling_group.my_asg.id]
  notifications = [
    "autoscaling:EC2_INSTANCE_LAUNCH",
    "autoscaling:EC2_INSTANCE_TERMINATE",
    "autoscaling:EC2_INSTANCE_LAUNCH_ERROR",
    "autoscaling:EC2_INSTANCE_TERMINATE_ERROR",
  ]
  topic_arn = aws_sns_topic.myasg_sns_topic.arn
}

# Target Tracking Scaling Policies
resource "aws_autoscaling_policy" "avg_cpu_policy_greater_than_xx" {
  name                      = "avg-cpu-policy-greater-than-xx"
  policy_type               = "TargetTrackingScaling"
  autoscaling_group_name    = aws_autoscaling_group.my_asg.id
  estimated_instance_warmup = 180

  target_tracking_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ASGAverageCPUUtilization"
    }
    target_value = 50.0
  }
}

resource "aws_autoscaling_policy" "alb_target_requests_greater_than_yy" {
  name                      = "alb-target-requests-greater-than-yy"
  policy_type               = "TargetTrackingScaling"
  autoscaling_group_name    = aws_autoscaling_group.my_asg.id
  estimated_instance_warmup = 120

  target_tracking_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ALBRequestCountPerTarget"
      resource_label         = "${var.alb_arn_suffix}/${var.target_group_arn_suffix}"
    }
    target_value = 10.0
  }
}

# Scheduled Actions
resource "aws_autoscaling_schedule" "increase_capacity_7am" {
  scheduled_action_name  = "increase-capacity-7am"
  min_size               = 2
  max_size               = 10
  desired_capacity       = 8
  start_time             = "2030-03-30T11:00:00Z"
  recurrence             = "00 09 * * *"
  autoscaling_group_name = aws_autoscaling_group.my_asg.id
}

resource "aws_autoscaling_schedule" "decrease_capacity_5pm" {
  scheduled_action_name  = "decrease-capacity-5pm"
  min_size               = 2
  max_size               = 10
  desired_capacity       = 2
  start_time             = "2030-03-30T21:00:00Z"
  recurrence             = "00 21 * * *"
  autoscaling_group_name = aws_autoscaling_group.my_asg.id
}

# Simple scaling policy for high CPU (used by CloudWatch alarm)
resource "aws_autoscaling_policy" "high_cpu" {
  name                   = "high-cpu"
  scaling_adjustment     = 4
  adjustment_type        = "ChangeInCapacity"
  cooldown               = 300
  autoscaling_group_name = aws_autoscaling_group.my_asg.name
}
