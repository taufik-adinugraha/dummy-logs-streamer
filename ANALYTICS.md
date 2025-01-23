# Log Analytics Dashboard Insights

This guide covers sample insights and queries for a log analytics dashboard using CSV, JSON, and Parquet logs stored in MinIO with Iceberg as the table format. These patterns help monitor system health, user activity, and error distributions.

## 1. Log Structures

### 1.1 CSV Logs (csv_app_logs)
- **Columns:**
  - event_time (timestamp)
  - log_level (INFO, DEBUG, WARNING, ERROR, CRITICAL)
  - user_id
  - action (login, logout, update, etc.)
  - description
- Best for: Application events, user actions, error frequency analysis

### 1.2 JSON Logs (json_web_logs)
- **Columns:**
  - timestamp
  - ip
  - method (GET, POST, etc.)
  - status (HTTP codes)
  - url
- Best for: Web server logs, traffic analysis, error response monitoring

### 1.3 Parquet Logs (parquet_sys_logs)
- **Columns:**
  - timestamp
  - hostname
  - severity (low, medium, high)
  - message
- Best for: System-level and security logs

## 2. Dashboard Insights

### 2.1 Log Volume Over Time
- **Visualization:** Line Chart
- **Purpose:** Track log events per time interval
- **Value:** Detect usage spikes/dips

### 2.2 Log Severity Distribution
- **Visualization:** Pie/Donut Chart
- **Purpose:** Compare log levels (INFO, WARNING, ERROR)
- **Value:** Monitor error frequency

### 2.3 Top 10 Users by Activity
- **Visualization:** Table
- **Purpose:** Identify most active users
- **Value:** Detect usage patterns or suspicious behavior

### 2.4 Top 10 IPs by Requests
- **Visualization:** Table
- **Purpose:** Track frequent API users
- **Value:** Identify potential abuse or heavy users

### 2.5 Error Rates Distribution
- **Visualization:** Pie/Bar Chart
- **Purpose:** Monitor HTTP status codes (2xx, 4xx, 5xx)
- **Value:** Track application health

### 2.6 System Severity Trend
- **Visualization:** Line/Area Chart
- **Purpose:** Track high-severity events over time
- **Value:** Early problem detection

### 2.7 Time-to-Action Analysis
- **Visualization:** Line Chart/Table
- **Purpose:** Measure time between user actions
- **Value:** Identify performance patterns

## 3. Example Queries

### 3.1 Trino SQL Examples

Using Iceberg tables:
- `nessie_catalog.logdb.csv_app_logs`
- `nessie_catalog.logdb.json_web_logs`
- `nessie_catalog.logdb.parquet_sys_logs`

#### 3.1.1 Log Volume Over Time
```sql
SELECT
  date_trunc('hour', event_time) AS hour_slot,
  COUNT(*) AS total_logs
FROM nessie_catalog.logdb.csv_app_logs
GROUP BY date_trunc('hour', event_time)
ORDER BY hour_slot;
```

#### 3.1.2 Log Severity Distribution
```sql
SELECT
  log_level,
  COUNT(*) AS lvl_count
FROM nessie_catalog.logdb.csv_app_logs
GROUP BY log_level
ORDER BY lvl_count DESC;
```

#### 3.1.3 Top 10 Users
```sql
SELECT
  user_id,
  COUNT(*) AS event_count
FROM nessie_catalog.logdb.csv_app_logs
GROUP BY user_id
ORDER BY event_count DESC
LIMIT 10;
```

#### 3.1.4 Top 10 IPs
```sql
SELECT
  ip,
  COUNT(*) AS request_count
FROM nessie_catalog.logdb.json_web_logs
GROUP BY ip
ORDER BY request_count DESC
LIMIT 10;
```

#### 3.1.5 HTTP Status Distribution
```sql
SELECT
  status,
  COUNT(*) AS status_count
FROM nessie_catalog.logdb.json_web_logs
GROUP BY status
ORDER BY status_count DESC;
```

#### 3.1.6 Severity Over Time
```sql
SELECT
  date_trunc('day', timestamp) AS day_slot,
  severity,
  COUNT(*) AS count_by_severity
FROM nessie_catalog.logdb.parquet_sys_logs
GROUP BY day_slot, severity
ORDER BY day_slot;
```

#### 3.1.7 High-Severity Log Details
```sql
SELECT
  hostname,
  severity,
  message
FROM nessie_catalog.logdb.parquet_sys_logs
WHERE severity = 'high'
ORDER BY timestamp DESC
LIMIT 50;
```

## 4. Summary

### Dashboard Insights
1. Volume over time
2. Severity / log-level distributions
3. Top users / IPs
4. Error rates / system issues
5. Response codes (for web logs)
6. Potential anomalies or spikes

### Query Patterns
- Aggregations (COUNT(*), GROUP BY)
- Time-based grouping (date_trunc())
- Filtering on severity or status codes

### Key Outcomes
- Real-time error and warning spike detection
- Suspicious activity monitoring (IPs/users)
- System health tracking via severity metrics
- Usage pattern analysis (popular endpoints and user actions)

Armed with these queries and visualizations, our log analytics dashboard becomes a central monitoring tool for application health, user behavior, and infrastructure status—all sourced from our unified MinIO + Iceberg data lake pipeline.
