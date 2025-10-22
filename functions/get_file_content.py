import os
from .config import MAX_CHARS
from google.genai import types


def get_file_content(working_directory, file_path):
    try:
        working_directory = os.path.abspath(working_directory)
        file_path = os.path.join(working_directory, file_path)
        file_path = os.path.abspath(file_path)

        if not file_path.startswith(working_directory):
            return f"Error: Cannot read \"{file_path}\" as it " + \
                    "is outside the permitted working directory"

        if not os.path.isfile(file_path):
            return "Error: File not found or is not a regular " + \
                    f"file: \"{file_path}\""

        with open(file_path) as file:
            contents = file.read(MAX_CHARS)
            if len(contents) > MAX_CHARS:
                contents += f"[...File \"{file_path}\" truncated" + \
                        f"at {MAX_CHARS} characters]"
            return contents
    except Exception as e:
        return f"Error: {e}"


schema_get_files_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Returns the contents of a file in a specified file." +
    f"Files over {MAX_CHARS} are truncated.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path":
            types.Schema(
                type=types.Type.STRING,
                description="The file to list the contents of relative " +
                "to the working directory. If one is not " +
                "provided or it doesn't exist, it " + "returns an error.",
            ),
        },
    ),
)
