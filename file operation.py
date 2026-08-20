# file operation - read content of file, get statements from file, handle file exceptions
file = None
try:
    file_name = "file1.txt"
    file = open(file_name, "r")
    content = file.read()
    print("File content:\n")
    print(content)
    file.seek(0)  # reset pointer to start
    lines = file.readlines()
    print("\nStatements in the file:")
    for i, line in enumerate(lines, start=1):
        print(f"{i}: {line.strip()}")
except FileNotFoundError:
    print("Error: The file does not exist. Please check the file name/path.")
except PermissionError:
    print("Error: You don't have permission to access this file.")
except IsADirectoryError:
    print("Error: The given name is a directory, not a file.")
except Exception as e:
    print("An unexpected error occurred:", e)
finally:
    if file is not None and not file.closed:
        file.close()
        print("\nFile closed successfully.")