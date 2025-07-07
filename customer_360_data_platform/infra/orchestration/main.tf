resource "aws_iam_role" "step_functions_role" {
  name = "customer_360_step_functions_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = {
        Service = "states.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_policy" "step_functions_policy" {
  name        = "customer_360_step_functions_policy"
  description = "IAM policy for Step Functions to invoke Lambda and Glue"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "lambda:InvokeFunction",
          "glue:StartJobRun",
          "glue:GetJobRun",
          "glue:GetJobRuns"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "step_functions_policy_attach" {
  role       = aws_iam_role.step_functions_role.name
  policy_arn = aws_iam_policy.step_functions_policy.arn
}

resource "aws_sfn_state_machine" "customer_360_state_machine" {
  name     = "customer_360_state_machine"
  role_arn = aws_iam_role.step_functions_role.arn

  definition = <<EOF
{
  "Comment": "Customer 360 Data Platform orchestration",
  "StartAt": "InvokeLambda",
  "States": {
    "InvokeLambda": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Parameters": {
        "FunctionName": "${aws_lambda_function.data_ingestion.arn}",
        "Payload": {}
      },
      "Next": "StartGlueJob"
    },
    "StartGlueJob": {
      "Type": "Task",
      "Resource": "arn:aws:states:::glue:startJobRun.sync",
      "Parameters": {
        "JobName": "${aws_glue_job.customer_360_etl_job.name}"
      },
      "End": true
    }
  }
}
EOF
}
