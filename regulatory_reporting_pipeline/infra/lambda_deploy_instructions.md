# Lambda Function Packaging and Deployment Instructions

## Packaging Lambda Functions

1. Navigate to the `lambda` directory:

```bash
cd regulatory_reporting_pipeline/lambda
```

2. Create deployment packages (zip files) for each Lambda function:

For `preprocess_lambda.py`:

```bash
zip preprocess_lambda.zip preprocess_lambda.py
```

For `report_generation_lambda.py`:

```bash
zip report_generation_lambda.zip report_generation_lambda.py
```

3. Move the zip files to the Terraform `infra` directory or update the Terraform `filename` paths accordingly.

## Deploying with Terraform

1. Initialize Terraform:

```bash
cd regulatory_reporting_pipeline/infra
terraform init
```

2. Review the plan:

```bash
terraform plan
```

3. Apply the plan to create resources:

```bash
terraform apply
```

## Notes

- Ensure your AWS credentials are configured with sufficient permissions.
- Update bucket names, ARNs, and other variables in `variables.tf` as needed.
- After deployment, update the Lambda environment variables or code with correct ARNs and endpoints.
- For Lambda dependencies beyond standard library, consider using Lambda Layers or container images.
