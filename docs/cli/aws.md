# CLI Reference — AWS

```
devops aws [COMMAND] [OPTIONS]
```

All AWS commands accept `--region` / `-r` to override the configured default region.

---

## list-instances

List EC2 instances.

```
devops aws list-instances [OPTIONS]
```

| Option | Short | Type | Default | Description |
|---|---|---|---|---|
| `--region` | `-r` | text | config default | AWS region |
| `--running` | | flag | false | Show only running instances |

**Examples**

```bash
# All instances in the default region
devops aws list-instances

# Only running instances in us-west-2
devops aws list-instances --region us-west-2 --running
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

**Examples**

```bash
devops aws describe-instance i-0abc123def456
devops aws describe-instance i-0abc123def456 --region eu-west-1
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

**Examples**

```bash
devops aws list-db-instances
devops aws list-db-instances --region ap-southeast-1
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

**Examples**

```bash
devops aws list-functions
devops aws list-functions --region us-east-1
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
| `--payload` | | text | None | JSON payload string |

**Examples**

```bash
# Invoke without payload
devops aws invoke-function my-function

# Invoke with a JSON payload
devops aws invoke-function my-function --payload '{"key":"value"}'

# Invoke cross-region
devops aws invoke-function my-function --region eu-central-1 --payload '{}'
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
| `--prefix` | | text | None | Filter by log group name prefix |

**Examples**

```bash
devops aws list-log-groups
devops aws list-log-groups --prefix /aws/lambda/
devops aws list-log-groups --region us-west-2 --prefix /ecs/
```
