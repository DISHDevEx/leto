import boto3


dynamodb = boto3.resource('dynamodb')

def merge_tables():
    # Define source and destination table names
    source_table_names = 'leto_original_file_size', 'leto_reduced_file_size', 'leto_reconstructed_file_size','leto_yolo','leto_mediapipe'  # Replace with your source table names
    destination_table_name = 'leto-merge-test'   # Replace with your destination table name

    # Initialize merged data list
    merged_data = []

    # Retrieve and merge data from source tables
    for table_name in source_table_names:
        table = dynamodb.Table(table_name)
        response = table.scan()
        #response = dynamodb.scan(TableName=table_name)
        items = response.get('Items', [])
        merged_data.extend(items)

    # Initialize DynamoDB for the new table
    new_dynamodb = boto3.resource('dynamodb')

    # Insert merged data into the new table
    for item in merged_data:
        put_request = {'PutRequest': {'Item': item}}
        write_request = {destination_table_name: [put_request]}
        new_dynamodb.batch_write_item(RequestItems=write_request)

    print(f'Merged data inserted into {destination_table_name}')
