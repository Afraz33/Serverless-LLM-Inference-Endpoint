# Serverless LLM Inference Endpoint

A minimal serverless API that performs LLM inference using Amazon Bedrock. The entire stack is defined in code and deployed automatically via GitHub Actions.

## Architecture

The architecture is straightforward: API Gateway receives requests, triggers a Lambda function, which calls Bedrock for inference and returns the response.

```
Client → API Gateway → Lambda → Bedrock (Llama 3.1) → Response
```

**Key Components:**

- **API Gateway**: Provides the REST endpoint (`/chat`)
- **Lambda**: Python function that handles request parsing and Bedrock communication
- **Bedrock**: Runs the Llama 3.1 8B model for text generation, currently mock inference is used due to non availability
- **CloudWatch**: Captures logs automatically

The Lambda receives a POST request with a JSON body containing a prompt, formats it according to given LLM's format, sends it to Bedrock, and returns the generated text.

**Scaling consideration**: Lambda can handle bursts pretty well, but if 10,000 requests hit at once, it'll try to spin up concurrent executions up to the account limit. Beyond that, requests get throttled. For high traffic, SQS can be added to control execution.

## Model Choice

I went with **Meta Llama 3.1 8B Instruct** , however currently mock inference is utilized due to non availability.

## IAM Permissions

The Lambda function needs minimal permissions to work. It only gets `bedrock:InvokeModel` scoped specifically to the Llama 3.1 model ARN.

For the GitHub Actions deployment, I created an IAM role that the workflow assumes using OIDC. This role has permissions to deploy CloudFormation stacks, manage Lambda functions and API Gateway resources. Using OIDC instead of access keys is more secure since there are no long-lived credentials stored in GitHub

## Cost Considerations

The main cost driver here is Bedrock inference.

Lambda and API Gateway costs are pretty negligible in comparison, probably under a dollar combined for moderate traffic. Lambda is billed on execution time (we're using 256MB memory with ~200ms execution time), and API Gateway charges per request.

The biggest thing to watch is token usage on the Bedrock side. Longer prompts and responses directly increase costs. If this were production, I'd add rate limiting to prevent unexpected bills from abuse or bugs

## CI/CD Pipeline

The GitHub Actions workflow runs on every push to main. It does two things:

1. **Quality check** - Runs flake8 linting to catch syntax errors
2. **Deploy** - Uses SAM CLI to build and deploy the Lambda and API Gateway

The deployment uses OIDC to authenticate with AWS so access keys are not needed. SAM handles all the CloudFormation complexity automatically.

## Possible Improvements

If I were taking this further, the priorities would be:

1. Add API key authentication via API Gateway
2. Implement rate limiting to control costs
3. **Handle high-traffic scenarios** - Right now if 10,000 requests hit simultaneously, Lambda will try to spin up that many concurrent executions (up to the account limit of 1000 by default). This could cause throttling errors and a massive Bedrock bill. Would need to add SQS for request queuing and process requests asynchronously to control concurrency
4. Add proper error handling and retry logic for Bedrock calls
5. Make model parameters configurable through request body
6. Set up CloudWatch alarms for cost anomalies and throttling
7. **Async processing for long-running requests** - For prompts that take longer to process, could use Step Functions or EventBridge to handle async workflows and notify users when complete
8. Consider caching for repeated queries with ElastiCache
9. Make it multi-region.

The current implementation is fully synchronous - API Gateway waits for Lambda, Lambda waits for Bedrock, then everything returns.

## Setup

To deploy this yourself:

1. Configure `AWS_ROLE_ARN` secret in GitHub with your OIDC role
2. Push to main branch
3. The API endpoint URL will be in the CloudFormation outputs

Test with:

```bash
curl -X POST https://your-api-url/Prod/chat/ \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello, how are you?"}'
```

---

**Note**: The code currently has a placeholder response. Uncomment the Bedrock API call in `app.py` once you have model access enabled in your AWS account.
