from typing import List
import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, Request, status, UploadFile, File
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from llama_index.core.chat_engine.types import BaseChatEngine
from llama_index.core.llms import ChatMessage, MessageRole
from app.engine import get_chat_engine
from app.engine.generate import generate_datasource

chat_router = r = APIRouter()


class _Message(BaseModel):
    role: MessageRole
    content: str


class _ChatData(BaseModel):
    messages: List[_Message]


@r.post("")
async def chat(
    request: Request,
    data: _ChatData,
    chat_engine: BaseChatEngine = Depends(get_chat_engine),
):
    # check preconditions and get last message
    if len(data.messages) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No messages provided",
        )
    lastMessage = data.messages.pop()
    if lastMessage.role != MessageRole.USER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Last message must be from user",
        )
    # convert messages coming from the request to type ChatMessage
    messages = [
        ChatMessage(
            role=m.role,
            content=m.content,
        )
        for m in data.messages
    ]

    # query chat engine
    response = await chat_engine.astream_chat(lastMessage.content, messages)

    # stream response
    async def event_generator():
        async for token in response.async_response_gen():
            # If client closes connection, stop sending events
            if await request.is_disconnected():
                break
            yield token

    return StreamingResponse(event_generator(), media_type="text/plain")

@r.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    file_location = f"data/{file.filename}"
    os.makedirs(os.path.dirname(file_location), exist_ok=True)
    with open(file_location, 'wb') as file_out:
        shutil.copyfileobj(file.file, file_out)
        generate_datasource()
    if os.path.exists(file_location):
        return JSONResponse(
            status_code=200, content={"message": "File uploaded successfully"}
        )
    else:
        return JSONResponse(status_code=500, content={"message": "File upload failed"})

# @r.post("/signin/")
# async def signin():
#     if username == password :
#         return JSONResponse(
#             status_code=200, content={"message": "Signed In successfully"}
#         )
#     else :
#         return JSONResponse(status_code=500, content={"message": "Sign In failed"})