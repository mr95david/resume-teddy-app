from datetime import datetime
import uuid
from typing import List, Optional
# from fa import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, Depends, Path
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.mongo import get_mongo_db
from app.models.schemas import QueryResponse
from app.services.document_service import process_docs
from app.models.constants import TYPE_FILE, TYPE_IMG
from app.services.ai_client import localAi_client 


process_router = APIRouter(
    # prefix="/process",
    tags=["document-processing"],
)

@process_router.get("/", summary="List all documents information", description="Returns all stored query results from MongoDB.")
async def list_documents():
    db = get_mongo_db()
    cursor = (db.document_queries.find().sort("timestamp", -1))

    results: List[QueryResponse] = []

    async for doc in cursor:
        doc.pop("_id", None)
        results.append(QueryResponse(**doc))

    return results

@process_router.get("/last/{limit}", summary="List the last N stored documents", description="Returns the most recent N stored query results from MongoDB.")
async def list_last_documents(
    limit: int = Path(..., gt=0, le=5, description="Number of last documents to retrieve (max 5)"),
):
    db = get_mongo_db()

    cursor = (
        db.document_queries
        .find()
        .sort("timestamp", -1)
        .limit(limit)
    )

    results: List[QueryResponse] = []

    async for doc in cursor:
        doc.pop("_id", None)
        results.append(QueryResponse(**doc))

    return results


# Endpoint de efecto principal
@process_router.post(
        "/upload", 
        response_model=QueryResponse,
        summary="Upload multiple documents files",
        description=(
            "Uploads one or more files (PDF, JPG, PNG), extracts their relevant content, "
            "and optionally sends the extracted information to the AI client to generate a summary "
            "or answer a user-specific query."
        ),
    )
async def upload_documents(
        user_id: str                    = Form(..., description="User identifier associated with the request."),
        files:   List[UploadFile]       = File(..., description="List of documents to be processed."),
        *,
        query:      Optional[str]       = Form(None, description="Optional user query for the AI model. If omitted, the system will generate a general summary of the uploaded documents."),
        request_id: Optional[str]       = Form(None, description="Optional request identifier. If not provided, one will be auto-generated.")
    ):
    if request_id is None: request_id = uuid.uuid4()
    start_time = datetime.now()
    documents_data: list = []

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
            
            documents_data.append(extract_info)
        # print(documents_data)
        # Ia processing
        if query and query.strip():
            ai_response = await localAi_client.default_ask(
                user_query=query,
                resume_list=documents_data,
            )
        else:
            ai_response = await localAi_client.sumarize_ask(
                resume_list=documents_data,
            )
        
        return_structure = QueryResponse(user_id=user_id, request_id=str(request_id), query=query, resultado=ai_response, timestamp=start_time)

        if ai_response is not None:
            db = get_mongo_db()
            doc_to_save = return_structure.model_dump()
            await db.document_queries.insert_one(doc_to_save)
        
        return return_structure

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error occurred. More details: {str(e)}"
        )

   