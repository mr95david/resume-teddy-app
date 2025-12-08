from fastapi import APIRouter
from fastapi import File
from fastapi import Form
from fastapi import HTTPException
from fastapi import UploadFile
# Owm libs
from app.models.schemas             import QueryResponse
from app.services.document_service  import process_docs
from app.models.constants           import TYPE_FILE
from app.models.constants           import TYPE_IMG

from app.services.ai_client         import localAi_client
# Typing libs
from typing import List
from typing import Optional
# Utilitaries
import uuid
from datetime import datetime

process_router = APIRouter(tags=["process"]) 

# Simulacion temporal
DOC_STORAGE = {}

@process_router.get("/", summary="List all documents information")
async def list_documents():
    # Simulacion temporal
    return {
        "process": list(DOC_STORAGE.values())
        }


@process_router.get("/{doc_id}", summary="Get a specific document information")
async def get_document(doc_id: str):
    # Simulacion temporal
    if doc_id not in DOC_STORAGE:
        raise HTTPException(status_code=404, detail="Document not found")

    return DOC_STORAGE[doc_id]


# Endpoint de efecto principal
@process_router.post(
        "/upload", 
        response_model=QueryResponse,
        summary="Upload multiple documents files"
    )
async def upload_documents(
        user_id: str                    = Form(...),
        files:   List[UploadFile]       = File(...),
        *,
        query:      Optional[str]       = Form(None),
        request_id: Optional[str]       = Form(None),
    ):
    if request_id is None: request_id = uuid.uuid4()
    star_time = datetime.now()
    document_data: list = []

    # TODO: Eliminar
    sample_return = QueryResponse(
        user_id="",
        request_id=str(request_id),
        query=None,
        resultado="Resultado final",
        timestamp=star_time
    )

    try:
        for idx, file in enumerate(files, start=1):
            _type_file = file.filename.split(".")[-1]
            
            # Type validation
            if _type_file.lower() not in TYPE_FILE and _type_file.lower() not in TYPE_IMG:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file type. Allowed formats are: PDF, JPG, and PNG."
                )
            
            extract_info = await process_docs(file)
            # extract_info["original_name"] = file.filename
            extract_info["idx_document"]  = str(idx) + " - " + file.filename 
            document_data.append(extract_info)

        # Ia processing
        if query is not None and query != "":
            response = await localAi_client.default_ask(user_query=query, resume_list=document_data)

        else:
            response = await localAi_client.sumarize_ask(resume_list=document_data)
        print(response)
        return sample_return

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error occurred. More details: {str(e)}"
        )

   