# app/handlers/comment_handler.py
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from app.models.user_and_product_model import *
from app.db import get_db_session

router = APIRouter(
    prefix="/products"
)

# 댓글 목록 조회
# 임시로 limit 10으로 설정
@router.get("/{product_id}/comments", status_code=200)
def get_comments(product_id: int,limit: int=10, session=Depends(get_db_session)) -> RespComments:
    if limit < 1 or limit > 10:
        limit = 10
    comments = session.exec(select(Comment).where(Comment.product_id == product_id).limit(limit)).all()
    return RespComments(comments=comments)

# 댓글 생성
@router.post("/{product_id}/comments", status_code=201)
def create_comment(product_id: int,comment_data: ReqComment, 
                session = Depends(get_db_session)) -> RespComments:
    new_comment = Comment(product_id=product_id,
                        user_id=comment_data.user_id,
                        content=comment_data.content)
    session.add(new_comment)
    session.commit()
    session.refresh(new_comment)
    return RespComments(comments=[new_comment])

# 댓글 수정
@router.put("/{product_id}/comments/{comment_id}", status_code=200)
def update_comment(product_id: int, comment_id: int,
                comment_data : ReqComment, session = Depends(get_db_session)) -> RespComments:
    comment = session.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=404, details="Comment not found")
    comment.content = comment_data.content
    session.commit()
    session.refresh(comment)
    return RespComments(comments=[comment])

# ! product_id 사용 안하는데 빼버릴까요?
# 댓글 삭제
@router.delete("/{product_id}/comments/{comment_id}", status_code=200)
def delete_comment(product_id: int, comment_id: int,
                session = Depends(get_db_session)):
    comment = session.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    session.delete(comment)
    session.commit()
    return {"message": "Comment deleted successfully"}
