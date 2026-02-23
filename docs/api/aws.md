# AWS API Reference

All AWS clients extend `AWSBaseClient`, which itself extends `IntegrationBaseClient`. Pass an optional `region` or `config` to any constructor.

```python
from devops_framework.aws.ec2 import EC2Client
from devops_framework.aws.rds import RDSClient
from devops_framework.aws.lambda_ import LambdaClient
from devops_framework.aws.cloudwatch import CloudWatchClient
```

---

## EC2Client

```python
EC2Client(region: str | None = None, config: Config | None = None)
```

### Methods

#### `list_instances(filters=None, instance_ids=None) -> list[dict]`

Return a flat list of instance dicts (without reservation wrappers).

```python
client = EC2Client(region="us-east-1")

# All instances
instances = client.list_instances()

# Specific instances
instances = client.list_instances(instance_ids=["i-0abc123", "i-0def456"])

# With filters
instances = client.list_instances(
    filters=[{"Name": "instance-state-name", "Values": ["running", "stopped"]}]
)
```

#### `get_instance(instance_id) -> dict`

Return a single instance dict. Raises `ResourceNotFoundError` if not found.

#### `list_running_instances() -> list[dict]`

Shortcut for `list_instances` filtered to `instance-state-name = running`.

#### `get_instance_status(instance_id) -> dict`

Return instance and system status checks for a single instance.

#### `stop_instance(instance_id) -> dict`

Stop an EC2 instance. Returns the `StoppingInstances[0]` response dict.

#### `start_instance(instance_id) -> dict`

Start an EC2 instance. Returns the `StartingInstances[0]` response dict.

---

## RDSClient

```python
RDSClient(region: str | None = None, config: Config | None = None)
```

### Methods

#### `list_instances(db_instance_identifier=None) -> list[dict]`

List RDS DB instances. Filter by identifier if provided.

#### `get_instance(db_instance_identifier) -> dict`

Return a single DB instance dict. Raises `ResourceNotFoundError` if not found.

#### `list_clusters(db_cluster_identifier=None) -> list[dict]`

List Aurora DB clusters. Filter by identifier if provided.

#### `get_cluster(db_cluster_identifier) -> dict`

Return a single DB cluster dict. Raises `ResourceNotFoundError` if not found.

#### `get_instance_events(db_instance_identifier, duration=1440) -> list[dict]`

Return recent events for a DB instance. `duration` is in minutes (default 24 h).

```python
client = RDSClient()
events = client.get_instance_events("mydb", duration=60)  # last 1 hour
for event in events:
    print(event["Message"], event["Date"])
```

---

## LambdaClient

```python
LambdaClient(region: str | None = None, config: Config | None = None)
```

### Methods

#### `list_functions() -> list[dict]`

Return all Lambda functions in the configured region (paginated).

#### `get_function(function_name) -> dict`

Return configuration and code location. Raises `ResourceNotFoundError` if the function does not exist.

#### `get_function_configuration(function_name) -> dict`

Return only the configuration (no code location). Raises `ResourceNotFoundError` if not found.

#### `invoke(function_name, payload=None, invocation_type="RequestResponse") -> dict`

Invoke a Lambda function synchronously and return parsed response.

- `payload` — optional `dict` serialised to JSON before sending.
- `invocation_type` — `"RequestResponse"` (sync) or `"Event"` (async).
- Raises `AWSAPIError` if the function returns a `FunctionError`.

```python
client = LambdaClient(region="eu-west-1")
result = client.invoke("my-function", payload={"key": "value"})
print(result["StatusCode"])   # 200
print(result["Payload"])      # parsed response body
```

---

## CloudWatchClient

```python
CloudWatchClient(region: str | None = None, config: Config | None = None)
```

### Metrics Methods

#### `get_metric_statistics(namespace, metric_name, dimensions, start_time, end_time, period=300, statistics=None) -> list[dict]`

Return sorted datapoints for a CloudWatch metric.

- `period` — aggregation period in seconds (default 5 min).
- `statistics` — list of `["Average"]`, `["Sum"]`, etc. Defaults to `["Average"]`.

```python
from datetime import datetime, timedelta, timezone
from devops_framework.aws.cloudwatch import CloudWatchClient

client = CloudWatchClient()
now = datetime.now(timezone.utc)
points = client.get_metric_statistics(
    namespace="AWS/EC2",
    metric_name="CPUUtilization",
    dimensions=[{"Name": "InstanceId", "Value": "i-0abc123"}],
    start_time=now - timedelta(hours=1),
    end_time=now,
    period=300,
    statistics=["Average", "Maximum"],
)
for p in points:
    print(p["Timestamp"], p["Average"])
```

#### `list_metrics(namespace=None, metric_name=None) -> list[dict]`

List CloudWatch metrics, optionally filtered by namespace and/or metric name.

### Log Methods

#### `list_log_groups(prefix=None) -> list[dict]`

List CloudWatch Log groups, optionally filtered by name prefix.

#### `get_log_events(log_group_name, log_stream_name, start_time=None, end_time=None, limit=100) -> list[dict]`

Return events from a specific log stream. Raises `ResourceNotFoundError` if the stream does not exist.

#### `filter_log_events(log_group_name, filter_pattern="", start_time=None, end_time=None, limit=100) -> list[dict]`

Search across all streams in a log group using a CloudWatch filter pattern.

```python
events = client.filter_log_events(
    log_group_name="/aws/lambda/my-function",
    filter_pattern="ERROR",
    limit=50,
)
for e in events:
    print(e["timestamp"], e["message"])
```
