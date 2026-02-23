# CLI Reference — AWS

```
devops aws [COMMAND] [OPTIONS]
```

All AWS commands accept:
- `--region` / `-r` to override the configured default region
- `--profile` / `-p` to use a specific AWS profile

---

## list-instances

List EC2 instances.

```
devops aws list-instances [OPTIONS]
```

| Option | Short | Type | Default | Description |
|---|---|---|---|---|
| `--region` | `-r` | text | config default | AWS region |
| `--profile` | `-p` | text | config default | AWS profile name |
| `--running` | | flag | false | Show only running instances |

**Examples**

```bash
# All instances in the default region
devops aws list-instances

# Only running instances in us-west-2
devops aws list-instances --region us-west-2 --running

# Using a specific profile
devops aws list-instances --profile production

# Combine region and profile
devops aws list-instances -r eu-west-1 -p staging
```

---

## describe-instance

Show full details for a single EC2 instance as JSON.

```
devops aws describe-instance INSTANCE_ID [OPTIONS]
```

| Argument | Description |
|---|---|
| `INSTANCE_ID` | EC2 instance ID (e.g. `i-0abc123def456`) |

| Option | Short | Type | Default | Description |
|---|---|---|---|---|
| `--region` | `-r` | text | config default | AWS region |
| `--profile` | `-p` | text | config default | AWS profile name |

**Examples**

```bash
devops aws describe-instance i-0abc123def456
devops aws describe-instance i-0abc123def456 --region eu-west-1
devops aws describe-instance i-0abc123def456 --profile production
```

---

## list-db-instances

List RDS DB instances.

```
devops aws list-db-instances [OPTIONS]
```

| Option | Short | Type | Default | Description |
|---|---|---|---|---|
| `--region` | `-r` | text | config default | AWS region |
| `--profile` | `-p` | text | config default | AWS profile name |

**Examples**

```bash
devops aws list-db-instances
devops aws list-db-instances --region ap-southeast-1
devops aws list-db-instances --profile production
```

---

## list-functions

List Lambda functions.

```
devops aws list-functions [OPTIONS]
```

| Option | Short | Type | Default | Description |
|---|---|---|---|---|
| `--region` | `-r` | text | config default | AWS region |
| `--profile` | `-p` | text | config default | AWS profile name |

**Examples**

```bash
devops aws list-functions
devops aws list-functions --region us-east-1
devops aws list-functions --profile dev-account
```

---

## invoke-function

Invoke a Lambda function synchronously and print the response as JSON.

```
devops aws invoke-function FUNCTION_NAME [OPTIONS]
```

| Argument | Description |
|---|---|
| `FUNCTION_NAME` | Lambda function name or ARN |

| Option | Short | Type | Default | Description |
|---|---|---|---|---|
| `--region` | `-r` | text | config default | AWS region |
| `--profile` | `-p` | text | config default | AWS profile name |
| `--payload` | | text | None | JSON payload string |

**Examples**

```bash
# Invoke without payload
devops aws invoke-function my-function

# Invoke with a JSON payload
devops aws invoke-function my-function --payload '{"key":"value"}'

# Invoke cross-region
devops aws invoke-function my-function --region eu-central-1 --payload '{}'

# Invoke using a specific profile
devops aws invoke-function my-function --profile production --payload '{"action":"update"}'
```

---

## list-log-groups

List CloudWatch Log groups.

```
devops aws list-log-groups [OPTIONS]
```

| Option | Short | Type | Default | Description |
|---|---|---|---|---|
| `--region` | `-r` | text | config default | AWS region |
| `--profile` | `-p` | text | config default | AWS profile name |
| `--prefix` | | text | None | Filter by log group name prefix |

**Examples**

```bash
devops aws list-log-groups
devops aws list-log-groups --prefix /aws/lambda/
devops aws list-log-groups --region us-west-2 --prefix /ecs/
devops aws list-log-groups --profile staging --prefix /api/
```
