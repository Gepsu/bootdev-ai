import os
from google.genai import types


def write_file(working_directory, file_path, content):
    try:
        working_directory = os.path.abspath(working_directory)
        file_path = os.path.join(working_directory, file_path)
        file_path = os.path.abspath(file_path)

        if not file_path.startswith(working_directory):
            return f"Error: Cannot write to \"{file_path}\" as it " + \
                    "is outside the permitted working directory"

        dirname = os.path.dirname(file_path)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

        with open(file_path, "w") as file:
            file.write(content)
    except Exception as e:
        return f"Error: {e}"

    return f"Successfully wrote to \"{file_path}\" ({len(content)} " + \
        "characters written)"


schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Writes and overwrites to a file",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path":
            types.Schema(
                type=types.Type.STRING,
                description="The file to write and overwrite to.",
            ),
            "content":
            types.Schema(
                type=types.Type.STRING,
                description="The content to be written to the file.",
            ),
        },
    ),
)
