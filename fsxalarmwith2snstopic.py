import boto3
import argparse

global SNS_CUSTOMER_ARN, SNS_SECONDARY_ARN
SNS_CUSTOMER_ARN = 'arn:aws:sns:us-east-1:010526239784:billing_alert'
SNS_SECONDARY_ARN = 'arn:aws:sns:us-east-1:010526239784:second'

def list_fsx_filesystems(region):
    print(f"Attempting to list FSx filesystems in region {region}")
    fsx = boto3.client('fsx', region_name=region)
    try:
        response = fsx.describe_file_systems()
        print(f"Found {len(response['FileSystems'])} file systems")
        return response['FileSystems']
    except Exception as e:
        print(f"Error listing file systems: {str(e)}")
        return []

def list_fsx_volumes(region, file_system_id):
    print(f"Attempting to list volumes for file system {file_system_id}")
    fsx = boto3.client('fsx', region_name=region)
    try:
        response = fsx.describe_volumes(Filters=[{'Name': 'file-system-id', 'Values': [file_system_id]}])
        print(f"Found {len(response['Volumes'])} volumes")
        return response['Volumes']
    except Exception as e:
        print(f"Error listing volumes: {str(e)}")
        return []

def create_volume_alarm(region, volume_id, volume_name, file_system_id):
    global SNS_CUSTOMER_ARN, SNS_SECONDARY_ARN
    print(f"Attempting to create alarm for volume {volume_id} ({volume_name})")
    session = boto3.Session(region_name=region)
    cw = session.client('cloudwatch')
    
    account_id = session.client('sts').get_caller_identity()['Account']
    print(f"Account ID: {account_id}")

    alarm_name = f"Primary FSx ONTAP Volume: {volume_name} Utilization Reached at 90%"
    alarm_description = f"Notify when Storage Capacity Utilization of FSx volume {volume_id} is greater than or equal to 90% for 1 datapoint within 5 minutes"

    try:
        cw.put_metric_alarm(
            AlarmName=alarm_name,
            ComparisonOperator='GreaterThanOrEqualToThreshold',
            EvaluationPeriods=1,
            MetricName='StorageCapacityUtilization',
            Namespace='AWS/FSx',
            Period=300,
            Statistic='Average',
            Threshold=90.0,
            ActionsEnabled=True,
            AlarmActions=[SNS_CUSTOMER_ARN, SNS_SECONDARY_ARN],
            OKActions=[SNS_CUSTOMER_ARN, SNS_SECONDARY_ARN],
            AlarmDescription=alarm_description,
            Dimensions=[
                {
                    'Name': 'VolumeId',
                    'Value': volume_id
                },
                {
                    'Name': 'FileSystemId',
                    'Value': file_system_id
                }
            ],
        )
        print(f"Successfully created alarm: {alarm_name}")
    except Exception as e:
        print(f"Error creating alarm: {str(e)}")

def create_filesystem_alarms(region, file_system_id):
    global SNS_CUSTOMER_ARN, SNS_SECONDARY_ARN
    print(f"Attempting to create alarms for file system {file_system_id}")
    session = boto3.Session(region_name=region)
    cw = session.client('cloudwatch')
    
    account_id = session.client('sts').get_caller_identity()['Account']
    print(f"Account ID: {account_id}")

    alarms = [
        {
            "name": f"FSx ONTAP CPU Utilization Reached at 90% Threshold for {file_system_id}",
            "description": f"Notify when CPU Utilization of FSx file system {file_system_id} is greater than or equal to 90% for 1 datapoint within 5 minutes",
            "metric": "CPUUtilization",
            "threshold": 90,
            "period": 300,
            "evaluation_periods": 1,
            "comparison_operator": "GreaterThanOrEqualToThreshold"
        },
        {
            "name": f"FSx ONTAP Disk throughput Utilization Reached at 90% Threshold for {file_system_id}",
            "description": f"Notify when File Server Disk Throughput Utilization of FSx file system {file_system_id} is greater than 90% for 1 datapoint within 15 minutes",
            "metric": "FileServerDiskThroughputUtilization",
            "threshold": 90,
            "period": 900,
            "evaluation_periods": 1,
            "comparison_operator": "GreaterThanThreshold"
        },
        {
            "name": f"FSx ONTAP Network throughput Utilization Reached at 90% Threshold for {file_system_id}",
            "description": f"Notify when Network Throughput Utilization of FSx file system {file_system_id} is greater than 90% for 1 datapoint within 15 minutes",
            "metric": "NetworkThroughputUtilization",
            "threshold": 90,
            "period": 900,
            "evaluation_periods": 1,
            "comparison_operator": "GreaterThanThreshold"
        }
    ]

    for alarm in alarms:
        try:
            cw.put_metric_alarm(
                AlarmName=alarm["name"],
                ComparisonOperator=alarm["comparison_operator"],
                EvaluationPeriods=alarm["evaluation_periods"],
                MetricName=alarm["metric"],
                Namespace='AWS/FSx',
                Period=alarm["period"],
                Statistic='Average',
                Threshold=alarm["threshold"],
                ActionsEnabled=True,
                AlarmActions=[SNS_CUSTOMER_ARN, SNS_SECONDARY_ARN],
                OKActions=[SNS_CUSTOMER_ARN, SNS_SECONDARY_ARN],
                AlarmDescription=alarm["description"],
                Dimensions=[
                    {
                        'Name': 'FileSystemId',
                        'Value': file_system_id
                    }
                ],
            )
            print(f"Successfully created alarm: {alarm['name']}")
        except Exception as e:
            print(f"Error creating alarm {alarm['name']}: {str(e)}")

def create_filesystem_capacity_alarms(region, file_system_id):
    global SNS_CUSTOMER_ARN, SNS_SECONDARY_ARN
    print(f"Attempting to create capacity alarms for file system {file_system_id}")
    session = boto3.Session(region_name=region)
    cw = session.client('cloudwatch')
    
    account_id = session.client('sts').get_caller_identity()['Account']
    print(f"Account ID: {account_id}")

    alarms = [
        {
            "name": f"FSx ONTAP SSD Capacity Reached at 75% Threshold for {file_system_id}",
            "description": f"Notify when Storage Capacity Utilization of FSx file system {file_system_id} is greater than or equal to 75% for 1 datapoint within 5 minutes",
            "threshold": 75.0
        },
        {
            "name": f"FSx ONTAP SSD Capacity Reached at 80% Threshold for {file_system_id}",
            "description": f"Notify when Storage Capacity Utilization of FSx file system {file_system_id} is greater than or equal to 80% for 1 datapoint within 5 minutes",
            "threshold": 80.0
        },
        {
            "name": f"FSx ONTAP SSD Capacity Reached at 90% Threshold for {file_system_id}",
            "description": f"Notify when Storage Capacity Utilization of FSx file system {file_system_id} is greater than or equal to 90% for 1 datapoint within 5 minutes",
            "threshold": 90.0
        }
    ]

    for alarm in alarms:
        try:
            cw.put_metric_alarm(
                AlarmName=alarm["name"],
                ComparisonOperator='GreaterThanOrEqualToThreshold',
                EvaluationPeriods=1,
                MetricName='StorageCapacityUtilization',
                Namespace='AWS/FSx',
                Period=300,
                Statistic='Average',
                Threshold=alarm["threshold"],
                ActionsEnabled=True,
                AlarmActions=[SNS_CUSTOMER_ARN, SNS_SECONDARY_ARN],
                OKActions=[SNS_CUSTOMER_ARN, SNS_SECONDARY_ARN],
                AlarmDescription=alarm["description"],
                Dimensions=[
                    {
                        'Name': 'StorageTier',
                        'Value': 'SSD'
                    },
                    {
                        'Name': 'FileSystemId',
                        'Value': file_system_id
                    },
                    {
                        'Name': 'DataType',
                        'Value': 'All'
                    }
                ],
            )
            print(f"Successfully created alarm: {alarm['name']}")
        except Exception as e:
            print(f"Error creating alarm {alarm['name']}: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='Create CloudWatch alarms for FSx volumes and file systems.')
    parser.add_argument('--region', required=True, help='The AWS region where the FSx file system is located.')
    args = parser.parse_args()

    print(f"Starting script with region: {args.region}")

    file_systems = list_fsx_filesystems(args.region)
    if not file_systems:
        print("No file systems found. Exiting.")
        return

    print("\nAvailable FSx File Systems:")
    for i, fs in enumerate(file_systems, 1):
        print(f"{i}. {fs['FileSystemId']} - {fs.get('Tags', [{'Key': 'Name', 'Value': 'N/A'}])[0]['Value']}")

    while True:
        try:
            fs_choice = int(input("\nEnter the number of the file system you want to work with: ")) - 1
            selected_fs = file_systems[fs_choice]
            break
        except (ValueError, IndexError):
            print("Invalid input. Please enter a valid number.")

    volumes = list_fsx_volumes(args.region, selected_fs['FileSystemId'])
    if not volumes:
        print("No volumes found for the selected file system.")
    else:
        print("\nAvailable Volumes:")
        for vol in volumes:
            print(f"VolumeId: {vol['VolumeId']}, Name: {vol['Name']}")

        volume_inputs = input("\nEnter the VolumeIds or Names for which you want to create alarms (comma-separated), or press Enter to skip: ").split(',')

        for volume_input in volume_inputs:
            volume_input = volume_input.strip()
            if volume_input:
                volume = next((v for v in volumes if v['VolumeId'] == volume_input or v['Name'] == volume_input), None)
                if volume:
                    create_volume_alarm(args.region, volume['VolumeId'], volume['Name'], selected_fs['FileSystemId'])
                else:
                    print(f"Volume '{volume_input}' not found in the selected file system.")

    create_filesystem_alarms(args.region, selected_fs['FileSystemId'])
    create_filesystem_capacity_alarms(args.region, selected_fs['FileSystemId'])

    print("Script execution completed.")

if __name__ == "__main__":
    main()