import boto3
import pandas as pd

dynamodb = boto3.resource('dynamodb')

def mergetablestodf():
    """
        Merge dynamodb tables into a dataframe

        Returns:
        ----------
            df: The dataframe with combined data from dynamoDB tablesß
    """

    # Define table names
    table_names = ['leto_original_file_size', 'leto_reduced_file_size', 'leto_reconstructed_file_size','leto_yolo','leto_mediapipe']  # Add your table names here

    # Retrieve data from each table
    table_data = []
    for table_name in table_names:
        table = dynamodb.Table(table_name)
        response = table.scan()
        #ßresponse = dynamodb.scan(TableName=table_name)
        items = response.get('Items', [])
        table_data.extend(items)
        
    # Convert DynamoDB data to a pandas DataFrame
    df = pd.DataFrame(table_data)

    return df

def main():
    mergetablestodf()


if __name__ == "__main__":
    main()