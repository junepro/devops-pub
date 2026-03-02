# ASG CPU Utilization CloudWatch Alarm
resource "aws_cloudwatch_metric_alarm" "app1_asg_cwa_cpu" {
  alarm_name          = "App1-ASG-CWA-CPUUtilization"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = "120"
  statistic           = "Average"
  threshold           = "80"

  dimensions = {
    AutoScalingGroupName = var.asg_name
  }

  alarm_description = "This metric monitors ec2 cpu utilization and triggers the ASG Scaling policy to scale-out if CPU is above 80%"

  ok_actions    = [var.sns_topic_arn]
  alarm_actions = [var.high_cpu_policy_arn, var.sns_topic_arn]
}

# ALB 4xx Errors CloudWatch Alarm
resource "aws_cloudwatch_metric_alarm" "alb_4xx_errors" {
  alarm_name          = "App1-ALB-HTTP-4xx-errors"
  comparison_operator = "GreaterThanThreshold"
  datapoints_to_alarm = "2"
  evaluation_periods  = "3"
  metric_name         = "HTTPCode_Target_4XX_Count"
  namespace           = "AWS/ApplicationELB"
  period              = "120"
  statistic           = "Sum"
  threshold           = "5"
  treat_missing_data  = "missing"

  dimensions = {
    LoadBalancer = var.alb_arn_suffix
  }

  alarm_description = "This metric monitors ALB HTTP 4xx errors and if they are above threshold, it sends a notification email"
  ok_actions        = [var.sns_topic_arn]
  alarm_actions     = [var.sns_topic_arn]
}

# CIS Log Group and Alarms
resource "aws_cloudwatch_log_group" "cis_log_group" {
  name = "cis-log-group-${var.random_suffix}"
}

module "all_cis_alarms" {
  source  = "terraform-aws-modules/cloudwatch/aws//modules/cis-alarms"
  version = "2.1.0"

  disabled_controls = ["DisableOrDeleteCMK", "VPCChanges"]
  log_group_name    = aws_cloudwatch_log_group.cis_log_group.name
  alarm_actions     = [var.sns_topic_arn]
  tags              = var.common_tags
}

# CloudWatch Synthetics - IAM
resource "aws_iam_policy" "cw_canary_iam_policy" {
  name        = "cw-canary-iam-policy"
  path        = "/"
  description = "CloudWatch Canary Synthetic IAM Policy"

  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Sid" : "VisualEditor0",
        "Effect" : "Allow",
        "Action" : "cloudwatch:PutMetricData",
        "Resource" : "*",
        "Condition" : {
          "StringEquals" : {
            "cloudwatch:namespace" : "CloudWatchSynthetics"
          }
        }
      },
      {
        "Sid" : "VisualEditor1",
        "Effect" : "Allow",
        "Action" : [
          "s3:PutObject",
          "logs:CreateLogStream",
          "s3:ListAllMyBuckets",
          "logs:CreateLogGroup",
          "logs:PutLogEvents",
          "s3:GetBucketLocation",
          "xray:PutTraceSegments"
        ],
        "Resource" : "*"
      }
    ]
  })
}

resource "aws_iam_role" "cw_canary_iam_role" {
  name                = "cw-canary-iam-role"
  description         = "CloudWatch Synthetics lambda execution role for running canaries"
  path                = "/service-role/"
  assume_role_policy  = "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"lambda.amazonaws.com\"},\"Action\":\"sts:AssumeRole\"}]}"
  managed_policy_arns = [aws_iam_policy.cw_canary_iam_policy.arn]
}

# S3 Bucket for Canary artifacts
resource "aws_s3_bucket" "cw_canary_bucket" {
  bucket        = "cw-canary-bucket-${var.random_suffix}"
  force_destroy = true

  tags = {
    Name        = "My bucket"
    Environment = "Dev"
  }
}

resource "aws_s3_bucket_ownership_controls" "example" {
  bucket = aws_s3_bucket.cw_canary_bucket.id
  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_acl" "example" {
  depends_on = [aws_s3_bucket_ownership_controls.example]
  bucket     = aws_s3_bucket.cw_canary_bucket.id
  acl        = "private"
}

# Synthetics Canary (zip path is relative to root - passed from caller)
resource "aws_synthetics_canary" "sswebsite2" {
  name                 = "sswebsite2"
  artifact_s3_location = "s3://${aws_s3_bucket.cw_canary_bucket.id}/sswebsite2"
  execution_role_arn   = aws_iam_role.cw_canary_iam_role.arn
  handler              = "sswebsite2.handler"
  zip_file             = var.synthetics_canary_zip_path
  runtime_version      = "syn-nodejs-puppeteer-6.0"
  start_canary         = true

  run_config {
    active_tracing     = true
    memory_in_mb       = 960
    timeout_in_seconds = 60
  }
  schedule {
    expression = "rate(1 minute)"
  }
}

resource "aws_cloudwatch_metric_alarm" "synthetics_alarm_app1" {
  alarm_name          = "Synthetics-Alarm-App1"
  comparison_operator = "LessThanThreshold"
  datapoints_to_alarm = "1"
  evaluation_periods  = "1"
  metric_name         = "SuccessPercent"
  namespace           = "CloudWatchSynthetics"
  period              = "300"
  statistic           = "Average"
  threshold           = "90"
  treat_missing_data  = "breaching"

  dimensions = {
    CanaryName = aws_synthetics_canary.sswebsite2.id
  }

  alarm_description = "Synthetics alarm metric: SuccessPercent LessThanThreshold 90"
  ok_actions        = [var.sns_topic_arn]
  alarm_actions     = [var.sns_topic_arn]
}
