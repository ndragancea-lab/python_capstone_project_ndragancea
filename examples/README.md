# DataForge Schema Examples

This directory contains ready-to-use data schema examples for common use cases.

## Available Schemas

### 1. User Activity Tracking
**File:** `user_activity_schema.json`

Tracks user actions on a website or application.

**Usage:**
```bash
python -m dataforge ./output --files_count=10 --file_name=user_activity \
  --data_schema=./examples/user_activity_schema.json
```

**Fields:**
- `user_id` - Unique user identifier (UUID)
- `session_id` - Session identifier (UUID)
- `action` - User action (login, logout, view_page, etc.)
- `page` - Page URL
- `duration_seconds` - Time spent (1-3600 seconds)
- `timestamp` - Event timestamp

---

### 2. E-commerce Orders
**File:** `ecommerce_orders_schema.json`

Simulates online store order data.

**Usage:**
```bash
python -m dataforge ./output --files_count=50 --file_name=orders \
  --data_schema=./examples/ecommerce_orders_schema.json --multiprocessing=4
```

**Fields:**
- `order_id` - Unique order ID (UUID)
- `customer_id` - Customer ID (1000-99999)
- `product_name` - Product name
- `category` - Product category
- `quantity` - Order quantity (1-10)
- `price` - Product price
- `discount_percent` - Discount (0-20%)
- `payment_method` - Payment type
- `status` - Order status
- `created_at` - Order timestamp

---

### 3. IoT Sensor Data
**File:** `iot_sensors_schema.json`

Industrial IoT sensor readings.

**Usage:**
```bash
python -m dataforge ./output --files_count=100 --data_lines=5000 \
  --file_name=sensor_data --data_schema=./examples/iot_sensors_schema.json \
  --multiprocessing=8
```

**Fields:**
- `sensor_id` - Sensor identifier (UUID)
- `device_type` - Sensor type
- `location` - Physical location
- `temperature_celsius` - Temperature (-20 to 50°C)
- `humidity_percent` - Humidity (10-90%)
- `pressure_hpa` - Air pressure (950-1050 hPa)
- `battery_level` - Battery (0-100%)
- `status` - Device status
- `timestamp` - Reading timestamp

---

### 4. Web Server Logs
**File:** `web_logs_schema.json`

HTTP request logs for web servers.

**Usage:**
```bash
python -m dataforge ./logs --files_count=20 --data_lines=10000 \
  --file_name=access_log --data_schema=./examples/web_logs_schema.json
```

**Fields:**
- `request_id` - Request identifier (UUID)
- `client_ip` - Client IP (UUID as placeholder)
- `http_method` - HTTP method
- `endpoint` - API endpoint
- `status_code` - HTTP status code
- `response_time_ms` - Response time (10-5000ms)
- `user_agent` - Browser/client
- `bytes_sent` - Response size
- `timestamp` - Request timestamp

---

### 5. Financial Transactions
**File:** `financial_transactions_schema.json`

Banking and payment transactions.

**Usage:**
```bash
python -m dataforge ./transactions --files_count=200 \
  --file_name=transaction --file_prefix=uuid \
  --data_schema=./examples/financial_transactions_schema.json \
  --multiprocessing=8
```

**Fields:**
- `transaction_id` - Transaction ID (UUID)
- `account_from` - Source account (6 digits)
- `account_to` - Destination account (6 digits)
- `amount_cents` - Amount in cents
- `currency` - Currency code
- `transaction_type` - Transaction type
- `category` - Transaction category
- `status` - Transaction status
- `fee_cents` - Transaction fee
- `description` - Optional description
- `timestamp` - Transaction timestamp

---

### 6. Social Media Posts
**File:** `social_media_schema.json`

Social media post analytics data.

**Usage:**
```bash
python -m dataforge ./social --files_count=30 --data_lines=2000 \
  --file_name=posts --data_schema=./examples/social_media_schema.json
```

**Fields:**
- `post_id` - Post identifier (UUID)
- `user_id` - User identifier (UUID)
- `content_type` - Content type (text, image, video, etc.)
- `likes_count` - Number of likes
- `comments_count` - Number of comments
- `shares_count` - Number of shares
- `sentiment` - Sentiment analysis (positive/neutral/negative)
- `hashtags_count` - Number of hashtags
- `mentions_count` - Number of mentions
- `is_verified` - Verified account flag
- `timestamp` - Post timestamp

---

## Tips for Using Schema Examples

### 1. Customize Schemas
Feel free to modify these schemas for your needs:
```json
{
  "custom_field": "str:[\"value1\",\"value2\"]",
  "another_field": "int:rand(min,max)"
}
```

### 2. Combine Multiple Runs
Generate different data sets:
```bash
# Generate morning data
python -m dataforge ./morning --data_schema=./examples/user_activity_schema.json

# Generate afternoon data
python -m dataforge ./afternoon --data_schema=./examples/user_activity_schema.json
```

### 3. Use Multiprocessing for Large Datasets
```bash
python -m dataforge ./bigdata --files_count=1000 --data_lines=10000 \
  --data_schema=./examples/iot_sensors_schema.json --multiprocessing=8
```

### 4. Test Before Large Generation
Always test with small datasets first:
```bash
# Test with console output
python -m dataforge . --files_count=0 --data_lines=5 \
  --data_schema=./examples/your_schema.json

# Test with few files
python -m dataforge ./test --files_count=2 --data_lines=10 \
  --data_schema=./examples/your_schema.json
```

---

## Creating Your Own Schemas

Schema format:
```json
{
  "field_name": "type:generation_instruction"
}
```

### Available Types
- `timestamp` - Unix timestamp
- `str` - String values
- `int` - Integer values

### Generation Instructions

**For strings (`str`):**
- `rand` - Random UUID
- `['val1','val2']` - Random choice from list
- `value` - Static value
- (empty) - Empty string

**For integers (`int`):**
- `rand` - Random [0-10000]
- `rand(min,max)` - Random in range
- `['1','2','3']` - Random choice from list
- `value` - Static value
- (empty) - None

**For timestamps (`timestamp`):**
- Any value - Current Unix timestamp

---

## Example Workflows

### Data Pipeline Testing
```bash
# Generate source data
python -m dataforge ./pipeline/input --files_count=100 \
  --data_schema=./examples/ecommerce_orders_schema.json

# Process data with your pipeline
./your_pipeline.sh ./pipeline/input ./pipeline/output

# Validate output
python -m dataforge ./pipeline/validation --files_count=10 \
  --data_schema=./examples/processed_orders_schema.json
```

### Performance Testing
```bash
# Small dataset
time python -m dataforge ./perf/small --files_count=10 --data_lines=1000

# Medium dataset
time python -m dataforge ./perf/medium --files_count=100 --data_lines=1000 --multiprocessing=4

# Large dataset
time python -m dataforge ./perf/large --files_count=1000 --data_lines=1000 --multiprocessing=8
```

---

## Need Help?

Refer to the main [README.md](../README.md) for detailed documentation.

