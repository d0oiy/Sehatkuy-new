from django.urls import path
from . import views

app_name = 'pharmacy'

urlpatterns = [
    # Medicine URLs
    path('medicines/', views.medicine_list, name='medicine_list'),
    path('medicines/<int:pk>/', views.medicine_detail, name='medicine_detail'),
    path('medicines/create/', views.medicine_create, name='medicine_create'),
    path('medicines/<int:pk>/edit/', views.medicine_update, name='medicine_update'),
    path('medicines/<int:pk>/delete/', views.medicine_delete, name='medicine_delete'),
    
    # Order URLs
    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),
    path('orders/create/', views.order_create, name='order_create'),
    path('orders/<int:order_id>/items/', views.order_items, name='order_items'),
    path('orders/<int:order_id>/items/<int:item_id>/delete/', views.order_item_delete, name='order_item_delete'),
    path('orders/<int:pk>/confirm/', views.order_confirm, name='order_confirm'),
    path('orders/<int:pk>/confirm-receipt/', views.order_confirm_receipt, name='order_confirm_receipt'),
    
    # Admin/Dokter viewing patient orders
    path('admin/patients/', views.patient_orders, name='patient_orders'),
    path('orders/<int:pk>/ipaymu/', views.create_ipaymu_payment, name='order_create_ipaymu'),
    path('orders/<int:pk>/qris/', views.create_ipaymu_qris, name='order_create_qris'),
    path('admin/patients/<int:patient_id>/orders/', views.patient_orders, name='patient_orders_detail'),
    path('admin/orders/<int:pk>/', views.admin_order_detail, name='admin_order_detail'),
    path('orders/<int:pk>/payment/', views.order_payment, name='order_payment'),
    path('orders/<int:pk>/cancel/', views.order_cancel, name='order_cancel'),
    path('admin/orders/<int:pk>/verify-payment/', views.admin_verify_payment, name='admin_verify_payment'),
    
    # Delivery & Map URLs
    path('delivery/<int:order_id>/map/', views.delivery_map, name='delivery_map'),
    path('delivery/<int:pk>/update/', views.delivery_update, name='delivery_update'),
    path('delivery/<int:pk>/status/', views.delivery_status_update, name='delivery_status_update'),
    
    # API URLs
    path('api/delivery/<int:delivery_id>/location/', views.api_delivery_location, name='api_delivery_location'),
]
