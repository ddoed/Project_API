# app/handlers/comment_handler.py
from fastapi import APIRouter, Body, Depends, HTTPException
from sqlmodel import select
from app.handlers.auth_handler import get_current_user
from app.models.user_and_product_model import *
from app.db import get_db_session
from app.services.comment_service import CommentService

router = APIRouter(prefix="/products")
comment_service = CommentService

# 댓글 목록 조회
# limit 10으로 설정
# 인증 불필요
@router.get("/{product_id}/comments", status_code=200)
def get_comments(
    product_id: int,
    limit: int=10, 
    session=Depends(get_db_session)
    ) -> RespComments:

    comments = comment_service.get_comments(session, product_id, limit)
    return RespComments(comments=comments)

# 댓글 생성 (인증 필요)
@router.post("/{product_id}/comments", status_code=201)
def create_comment(
    product_id: int, 
    content: str = Body(..., description="댓글 내용"),
    current_user: User = Depends(get_current_user),
    session = Depends(get_db_session)
    ) -> RespComments:
    
    new_comment = comment_service.create_comment(session, product_id, current_user.id, content)
    return RespComments(comments=[new_comment])

# (주의) product_id는 수정, 삭제에 사용되지 않지만 Path의 일관성을 위해

# 댓글 수정 (인증 필요)
@router.put("/{product_id}/comments/{comment_id}", status_code=200)
def update_comment(
    product_id: int, 
    comment_id: int,
    content: str = Body(..., description="수정할 댓글 내용"),
    current_user: User = Depends(get_current_user),
    session = Depends(get_db_session)
    ) -> RespComments:
    
    updated_comment = comment_service.update_comment(session, comment_id, current_user.id, content)
    return RespComments(comments=[updated_comment])


# 댓글 삭제 (인증 필요)
@router.delete("/{product_id}/comments/{comment_id}", status_code=200)
def delete_comment(
    product_id: int, 
    comment_id: int,
    current_user: User = Depends(get_current_user),
    session = Depends(get_db_session)):
    
    result = comment_service.delete_comment(session, comment_id, current_user.id)
    return result
