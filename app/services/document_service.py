# NOTE: This module have all functions to process the resume documents
# Typing libs
from fastapi import UploadFile
from typing  import Any
from typing  import Union

# Validation functions
def validate_and_transform_doc(upload_doc: Union[str, UploadFile]):
    pass