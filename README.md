# AWS FSx Monitoring Scripts

A collection of Python scripts for setting up comprehensive CloudWatch monitoring and alerting for AWS FSx file systems. These scripts help automate the creation of various performance and capacity alarms for FSx ONTAP systems.

## Features

- **Volume Monitoring**
  - Storage capacity utilization alerts (90% threshold)
  - Automatic alarm creation for multiple volumes
  - Custom naming based on volume identifiers

- **File System Monitoring**
  - CPU Utilization (90% threshold)
  - Disk Throughput Utilization (90% threshold)
  - Network Throughput Utilization (90% threshold)
  - SSD Storage Capacity monitoring with multiple thresholds (75%, 80%, 90%)

- **Flexible SNS Integration**
  - Support for multiple SNS topics
  - Configurable notification targets
  - OK/Alarm state notifications

## Prerequisites

- Python 3.6 or higher
- AWS credentials configured (`~/.aws/credentials` or environment variables)
- Required Python packages:
  ```
  boto3
  argparse
  ```
- Appropriate AWS IAM permissions:
  - `fsx:DescribeFileSystems`
  - `fsx:DescribeVolumes`
  - `cloudwatch:PutMetricAlarm`
  - `sns:ListTopics`
  - `sts:GetCallerIdentity`

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd aws-fsx-monitoring
   ```

2. Install required packages:
   ```bash
   pip install boto3 argparse
   ```

## Usage

### Basic Usage

Run the script with the required region parameter:

```bash
python fsx_monitoring.py --region us-east-1
```

### Interactive Process

1. The script will:
   - List available FSx file systems
   - Prompt for file system selection
   - Display available volumes
   - Allow volume selection for monitoring
   - Create configured alarms

2. Follow the interactive prompts to:
   - Select target FSx file system
   - Choose volumes for monitoring
   - Confirm alarm creation

### Available Scripts

1. `fsx_monitoring.py`: Basic monitoring with single SNS topic
2. `fsx_monitoring_multi_sns.py`: Enhanced version with multiple SNS topic support
3. `fsx_monitoring_interactive_sns.py`: Interactive SNS topic selection

## Alarm Configurations

### Volume Alarms
- **Metric**: StorageCapacityUtilization
- **Threshold**: 90%
- **Period**: 5 minutes
- **Evaluation**: 1 datapoint

### File System Alarms
- **CPU Utilization**
  - Threshold: 90%
  - Period: 5 minutes
  
- **Disk Throughput**
  - Threshold: 90%
  - Period: 15 minutes
  
- **Network Throughput**
  - Threshold: 90%
  - Period: 15 minutes

### Storage Capacity Alarms
- Multiple thresholds: 75%, 80%, 90%
- Period: 5 minutes
- Specific to SSD storage tier

## Customization

### SNS Topics
Modify the SNS ARNs in the script:
```python
SNS_CUSTOMER_ARN = 'your-sns-arn'
SNS_SECONDARY_ARN = 'your-secondary-sns-arn'
```

### Alarm Thresholds
Adjust threshold values in the respective functions:
```python
"threshold": 90  # Modify this value
```

## Error Handling

The scripts include comprehensive error handling for:
- AWS API failures
- Invalid user inputs
- Resource not found scenarios
- Permission issues

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request


## Security Notes

- Never commit AWS credentials
- Use IAM roles when possible
- Regularly rotate access keys
- Follow AWS security best practices