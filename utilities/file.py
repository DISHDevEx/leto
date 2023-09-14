
def file(td, ):
    # Specify the directory and filename
    directory = td
    filename = "example.txt"

    # Text to write to the file
    text_to_write = "Hello, this is some sample text."

    # Combine the directory and filename to create the full path
    file_path = f"{directory}/{filename}"
    print(file_path)

    # Create and open the file in write mode ('w')
    with open(file_path, 'w') as file:
        # Write the text to the file
        file.write(text_to_write)

    # Now, let's read the text from the file and print it to the console
    with open(file_path, 'r') as file:
        # Read the contents of the file
        file_contents = file.read()

    # Print the text from the file to the console
    print("Text from the file:")
    print(file_contents)
