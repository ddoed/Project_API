# app/handlers/comment_handler.py
from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlmodel import select
from app.handlers.auth_handler import get_current_user
from app.models.user_and_product_model import *
from app.db import get_db_session
from app.services.comment_service import CommentService

router = APIRouter(prefix="/api/comments")
comment_service = CommentService()

# 댓글 목록 조회
# limit 10
# 인증 불필요
@router.get("/", status_code=200)
def get_comments(
    product_id: int = Query(..., description="조회할 상품의 ID"),
    limit: int = Query(10, le=10, description="최대 조회 개수"),
    session=Depends(get_db_session)
    ) -> RespComments:

    comments = comment_service.get_comments(session, product_id, limit)
    return RespComments(comments=comments)

# 댓글 생성 (인증 필요)
@router.post("/", status_code=201)
def create_comment(
    product_id: int = Body(...), 
    content: str = Body(..., description="댓글 내용"),
    current_user: User = Depends(get_current_user),
    session = Depends(get_db_session)
    ) -> RespComments:
    
    new_comment = comment_service.create_comment(session, product_id, current_user.id, content)
    return RespComments(comments=[new_comment])


# 댓글 수정 (인증 필요)
@router.put("/{comment_id}", status_code=200)
def update_comment(
    comment_id: int,
    comment_data: CommentUpdate,
    current_user: User = Depends(get_current_user),
    session = Depends(get_db_session)
    ) -> RespComments:
    
    updated_comment = comment_service.update_comment(session, comment_id, current_user.id, comment_data.content)
    return RespComments(comments=[updated_comment])


# 댓글 삭제 (인증 필요)
@router.delete("/{comment_id}", status_code=200)
def delete_comment(
    comment_id: int,
    current_user: User = Depends(get_current_user),
    session = Depends(get_db_session)):
    
    result = comment_service.delete_comment(session, comment_id, current_user.id)
    return result
