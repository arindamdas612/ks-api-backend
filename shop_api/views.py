import json

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.authentication import TokenAuthentication
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, FileUploadParser

from .models import Category, Product, ProductImage, ProductSpecification
from .serializers import CategorySerializer, ProductImageSerializer


class CategoryAdminViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()

    authentication_classes = (TokenAuthentication,)
    serializer_class = CategorySerializer
    permission_classes = (
        IsAuthenticated,
        IsAdminUser,
    )


class ProductCreateAdminApiView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, IsAdminUser,)
    parser_classes = (MultiPartParser, FormParser, FileUploadParser,)

    def get(self, request, format=None):
        response_data = {
            'message_code': 0,

        }
        products = []
        all_products = Product.objects.all()
        for product in all_products:
            product_data = {
                'id': product.id,
                'title': product.title,
                'categoryId': product.category.id,
                'qty': product.qty,
                'markedPrice': product.marked_price,
                'isActive': product.is_active,
                'imageUrls': [q.get_image_url() for q in ProductImage.objects.filter(
                    product=product)],
                'specs': [{'key': q.spec_title, 'value': q.spec_value} for q in ProductSpecification.objects.filter(product=product)]
            }
            products.append(product_data)

        response_data['message_code'] = 1
        response_data['products'] = products

        return Response(response_data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        respnse_data = {
            'message_code': 0,
        }
        try:
            title = request.POST.get('title')
            category_id = int(request.POST.get('categoryId'))
            is_active = True if request.POST.get('isActive') == 'y' else False
            marked_price = float(request.POST.get('markedPrice'))
            qty = int(request.POST.get('qty'))
            specs = request.POST.get('specs')
            photo = request.FILES
        except:
            respnse_data = {
                'message_code': 0,
                'error': 'Invalid data',
            }
            return Response(respnse_data, status=status.HTTP_406_NOT_ACCEPTABLE)
        finally:
            prodCategory = Category.objects.get(pk=category_id)
            new_product = Product(
                category=prodCategory,
                title=title, is_active=is_active, marked_price=marked_price, qty=qty,
            )
            new_product.save()
            image_serializer = ProductImageSerializer(
                data=request.data, context={'prod_id': new_product.id})
            if image_serializer.is_valid():
                images = image_serializer.save()
                respnse_data['productId'] = new_product.id

                image_urls = [q.get_image_url() for q in ProductImage.objects.filter(
                    product=new_product)]
                respnse_data['image_urls'] = image_urls

                spec_dict = json.loads(specs)
                for productSpecification in spec_dict:
                    ProductSpecification.objects.create(
                        product=new_product, spec_title=productSpecification['key'], spec_value=productSpecification['value'])

                respnse_data['message_code'] = 1
                return Response(respnse_data, status=status.HTTP_201_CREATED)

            else:
                respnse_data = {
                    'message_code': 0,
                    'error': 'Invalid Images',
                }

                return Response(respnse_data, status=status.HTTP_406_NOT_ACCEPTABLE)

    def put(self, request, format=None):
        response_data = {
            'message_code': 1,
        }
        try:
            product_id = int(request.data.get('id'))
            product = Product.objects.get(pk=product_id)
            image_serializer = ProductImageSerializer(
                data=request.data, context={'prod_id': product_id})
            if image_serializer.is_valid():
                product_images = ProductImage.objects.filter(product=product)
                print('product retrived', product)
                for prod_img in product_images:
                    prod_img.delete()
                print('product image deleted',
                      ProductImage.objects.filter(product=product))
                images = image_serializer.save()
                print('product_saved', ProductImage.objects.filter(product=product))
                image_urls = [q.get_image_url() for q in ProductImage.objects.filter(
                    product=product)]
                print(image_urls)
                response_data['image_urls'] = image_urls
                response_data['message'] = 'Update Success'
                print(response_data['image_urls'])
                return Response(response_data, status=status.HTTP_202_ACCEPTED)
            else:
                response_data = {
                    'message_code': 0,
                    'error': 'Invalid Images'
                }
                return Response(response_data, status=status.HTTP_403_FORBIDDEN)

        except:
            response_data = {
                'message_code': 0,
                'error': 'Invalid Product update request'
            }
            return Response(response_data, status=status.HTTP_406_NOT_ACCEPTABLE)


class ProductUpdateAdminApiView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, IsAdminUser,)

    def post(self, request, format=None):
        response_data = {
            'message_code': 1,
        }
        try:
            id = int(request.data.get('id'))
            title = request.data.get('title')
            category_id = int(request.data.get('categoryId'))
            is_active = True if request.data.get('isActive') == 'y' else False
            marked_price = float(request.data.get('markedPrice'))
            qty = int(request.data.get('qty'))
            product_to_update = Product.objects.get(pk=id)
            product_to_update.title = title
            product_to_update.is_active = is_active
            product_to_update.marked_price = marked_price
            product_to_update.qty = qty
            # if category_id != product_to_update.category.id:
            #     product_to_update.category = Category.objects.get(
            #         pk=category_id)
            product_to_update.save()
            response_data['message'] = 'Update Success'

            return Response(response_data, status=status.HTTP_202_ACCEPTED)
        except:
            response_data = {
                'message_code': 0,
                'error': 'Invalid Product update request'
            }
            return Response(response_data, status=status.HTTP_406_NOT_ACCEPTABLE)

    def patch(self, request, format=None):
        response_data = {
            'message_code': 1,
        }
        try:
            id = int(request.data.get('id'))
            specs = request.data.get('specs')

            product = Product.objects.get(pk=id)
            specifications = ProductSpecification.objects.filter(
                product=product)
            for spec in specifications:
                spec.delete()

            spec_dict = json.loads(specs)
            for productSpecification in spec_dict:
                ProductSpecification.objects.create(
                    product=product, spec_title=productSpecification['key'], spec_value=productSpecification['value'])

            response_data['message'] = 'Update Success'

            return Response(response_data, status=status.HTTP_202_ACCEPTED)

        except:
            response_data = {
                'message_code': 0,
                'error': 'Invalid Product update request'
            }
            return Response(response_data, status=status.HTTP_406_NOT_ACCEPTABLE)

    def delete(self, request, format=None):
        response_data = {
            'message_code': 1,
        }
        try:
            id = int(request.GET.get('id'))
            product = Product.objects.get(pk=id)
            product.delete()
            response_data['message'] = 'Product Removed'
            return Response(response_data, status=status.HTTP_200_OK)
        except:
            response_data = {
                'message_code': 0,
                'message': 'Invalid data, could not delete Product'
            }
            return Response(response_data, status=status.HTTP_406_NOT_ACCEPTABLE)
