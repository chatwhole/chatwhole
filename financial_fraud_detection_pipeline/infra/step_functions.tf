resource "aws_iam_role" "step_functions_role" {
  name = "step_functions_execution_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "states.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "step_functions_policy_attach" {
  role       = aws_iam_role.step_functions_role.name
  policy_arn = "arn:aws:iam::aws:policy/AWSStepFunctionsFullAccess"
}

resource "aws_sfn_state_machine" "fraud_detection_workflow" {
  name     = "fraud-detection-workflow"
  role_arn = aws_iam_role.step_functions_role.arn

  definition = <<EOF
{
  "Comment": "Orchestration for fraud detection pipeline",
  "StartAt": "ModelRetraining",
  "States": {
    "ModelRetraining": {
      "Type": "Task",
      "Resource": "arn:aws:states:::sagemaker:createTrainingJob.sync",
      "Parameters": {
        "TrainingJobName.$": "States.Format('fraud-model-retrain-{}', $$.Execution.StartTime)",
        "AlgorithmSpecification": {
          "TrainingImage": "382416733822.dkr.ecr.us-east-1.amazonaws.com/randomcutforest:1",
          "TrainingInputMode": "File"
        },
        "RoleArn": "${aws_iam_role.lambda_role.arn}",
        "InputDataConfig": [
          {
            "ChannelName": "train",
            "DataSource": {
              "S3DataSource": {
                "S3DataType": "S3Prefix",
                "S3Uri": "s3://${aws_s3_bucket.processed_data.bucket}/training/",
                "S3DataDistributionType": "FullyReplicated"
              }
            }
          }
        ],
        "OutputDataConfig": {
          "S3OutputPath": "s3://${aws_s3_bucket.model_artifacts.bucket}/output/"
        },
        "ResourceConfig": {
          "InstanceCount": 1,
          "InstanceType": "ml.m5.large",
          "VolumeSizeInGB": 10
        },
        "StoppingCondition": {
          "MaxRuntimeInSeconds": 3600
        }
      },
      "Next": "ETLJob"
    },
    "ETLJob": {
      "Type": "Task",
      "Resource": "arn:aws:states:::glue:startJobRun.sync",
      "Parameters": {
        "JobName": "${aws_glue_job.fraud_etl_job.name}"
      },
      "End": true
    }
  }
}
EOF
}
