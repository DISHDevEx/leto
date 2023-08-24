import boto3
import pandas as pd

dynamodb = boto3.client('dynamodb')

def mergetablestodf():
    # Define table names
    table_names = ['leto_original_file_size', 'leto_reduced_file_size', 'leto_reconstructed_file_size','leto_yolo','leto_mediapipe']  # Add your table names here

    # Retrieve data from each table

    dataframes = pd.DataFrame()
    for table_name in table_names:
        response = dynamodb.scan(TableName=table_name)
        items = response.get('Items',[])
        table_data = []
        for item in items:
            row = {key: val['S'] for key, val in item.items()}    
            table_data.append(row)    
        if len(table_data):
            # Convert DynamoDB data to a pandas DataFrame
            df = pd.DataFrame(table_data)
            if len(dataframes) ==0:
                # Copy the first table data
                dataframes = df
            else:
                # Merge table data
                dataframes=pd.merge(dataframes,df,on='video_location',how='outer')
            df = pd.DataFrame()
    return df

def main():
    mergetablestodf()


if __name__ == "__main__":
    main()