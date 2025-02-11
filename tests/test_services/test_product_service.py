import unittest
from app.services.product_service import ProductService

class TestProductService(unittest.TestCase):
    def test_get_product(self):
        # 없는 product_id를 입력한 경우
        pass
    def test_get_products(self):
        # 쿼리 검색 테스트
        # 필터링 테스트
        # 정렬 테스트
        # page, limit 테스트
        pass
    

    def test_create_product(self):
        # DB에 잘 저장되는지 확인
        # user_id가 존재하는가 -> 핸들링 필요
        # category_id가 존재하는가 -> 핸들링 필요
        pass

    def test_update_product(self):
        # DB에 잘 저장되는지 확인
        # 존재하지 않는 product_id를 입력한 경우
        # Product.user_id와 User.id가 다른 경우 -> 에러 핸들링 필요
        pass
    
    def test_delete_product(self):
        # 없는 product_id를 입력한 경우
        # Product.user_id와 User.id가 다른 경우
        # list[ProductImage]가 비어있지 않은 경우
        # 연결되어 있는 다른 테이블이 있는 경우 -> 에러 핸들링 필요
        pass
    
    def test_upload_product_image(self):
        #
        pass

    def test_delete_product_image(self):
        # 없는 product_id를 입력한 경우
        # 없는 image_id를 입력한 경우
        # Product.user_id와 User.id가 다른 경우 -> 에러 핸들링 필요
        pass