from django.urls import path 
from . import views
urlpatterns= [
    path('cod',views.cod,name='cod'),

    path('review/<int:id>/',views.review,name='review'),
    path('order_history/',views.order_history,name='order_history'),
    path('delete_address/<int:id>/',views.delete_address,name='delete_address'),

    path('profile/',views.profile,name='profile'),
    path('edit_profile/<int:id>/',views.edit_profile,name='edit_profile'),

    path('wish_list/',views.wish_list,name='wish_list'),
    path('wish_add/<int:id>/',views.wish_add,name='wish_add'),
    path('remove_wish_list/<int:product_id>/',views.remove_wish_list,name='remove_wish_list'),

    path('payment_status/',views.payment_status,name='payment_status'),
    path('confirm_payment/',views.payment,name='confirm_payment'),
    path('payment/',views.payment,name='payment'),
    path('place_order/',views.place_order,name='place_order'),
    path('checkout/',views.checkout,name='checkout'),

    path('search/',views.search,name='search'),

    path('cart/',views.cart,name='cart'),
    path('add_cart/<int:product_id>/',views.add_cart,name='add_cart'),
    path('remove_cart/<int:product_id>/<int:cart_item_id>/',views.remove_cart,name='remove_cart'),
    path('remove_cart_item/<int:product_id>/<int:cart_item_id>/',views.remove_cart_item,name='remove_cart_item'),

    path('register/',views.register,name='register'),
    path('login/',views.login,name='login'),
    path('',views.home,name='home'),
    path('logout/',views.logout,name='logout'),

    path('activate/<uidb64>/<token>/',views.activate,name='activate'),
    path('forgotPassword/',views.forgotPassword,name='forgotPassword'),
    path('resetpassword_validate/<uidb64>/<token>/',views.resetpassword_validate,name='resetpassword_validate'),
    path('resetPassword/',views.resetPassword,name='resetPassword'),
    path('verify_code/', views.verify_code,name='verify'),

    path('shop/',views.shop,name='shop'),
    path('category/<slug:category_slug>/',views.store,name='products_by_category'),
    path('category/<slug:category_slug>/<slug:subcategory_slug>/',views.sub_categories,name='products_by_subCategory'),
    path('category/<slug:category_slug>/<slug:subcategory_slug>/<slug:pro_slug>/',views.product_detail,name='product_detail')
    ]