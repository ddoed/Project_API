from fastapi import HTTPException
from app.models.user_and_product_model import *
from sqlmodel import Session, select

class CommentService:
    # 댓글 ID로 댓글 조회
    def get_comment_by_id(self, db: Session, comment_id: int):
        comment = db.get(Comment, comment_id)
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")
        return comment
    
    # 댓글 작성자인지 확인
    def check_comment_owner(self, comment: Comment, user_id: int):
        if comment.user_id != user_id:
            raise HTTPException(status_code=403, detail="Permission denied")
    
    # 특정 상품의 댓글 목록 조회
    def get_comments(self, db: Session, product_id: int, limit: int = 10):
        if limit < 1 or limit > 10:
            limit = 10
        comments = db.exec(select(Comment).where(Comment.product_id == product_id).limit(limit)).all()
        return comments
    
    # 댓글 생성
    def create_comment(self, db: Session, product_id: int, user_id: int, content: str):
        new_comment = Comment(product_id=product_id, user_id=user_id, content=content)
        db.add(new_comment)
        db.commit()
        db.refresh(new_comment)
        return new_comment
    
    # 댓글 수정
    def update_comment(self, db: Session, comment_id: int, user_id: int, content: str):
        comment = self.get_comment_by_id(db, comment_id)
        self.check_comment_owner(comment, user_id)

        comment.content = content
        comment.last_modified = datetime.now()
        db.commit()
        db.refresh(comment)
        return comment
    
    # 댓글 삭제
    def delete_comment(self, db: Session, comment_id: int, user_id: int):
        comment = self.get_comment_by_id(db, comment_id)
        self.check_comment_owner(comment, user_id)
        
        db.delete(comment)
        db.commit()
        return {"message": "Comment deleted successfully"}

