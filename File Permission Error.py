# file permission error - write into file that doesn't have write permission
try:
    file_name = "file.txt"
    file = open(file_name, "w")
    content = input("Enter content to write into the file: ")
    x = file.write(content)
    file.close()
    print("Content written successfully.")
except PermissionError:
    print("Error: You do not have permission to write to this file.")
except FileNotFoundError:
    print("Error: The file or path does not exist.")
except Exception as e:
    print("An unexpected error occurred:", e)
finally:
    try:
        read_file = open(file_name, "r")
        read_content = read_file.read()
        read_file.close()
        print("\nCurrent content of the file:")
        print(read_content)
    except Exception as e:
        print("Could not read the file:", e)