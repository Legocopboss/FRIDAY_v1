def file_access(filename, mode, data=None):
    try:
        if mode == "read":
            with open(filename, "r") as file:
                content = file.read()
                file.close()
                return content
        elif mode == "write":
            with open(filename, "w") as file:
                file.write(data)
                file.close()
                return "Data written successfully."
        else:
            return "Invalid mode. Please choose either 'read' or 'write'."
    except FileNotFoundError:
        return "File not found."
    except PermissionError:
        return "Permission denied to access the file."