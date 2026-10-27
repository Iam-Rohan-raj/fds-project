from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('shorten/', views.shorten_url, name='shorten_url'),
    path('links/', views.all_urls, name='all_urls'),
    path('links/<int:pk>/', views.url_detail, name='url_detail'),
    path('links/<int:pk>/delete/', views.delete_url, name='delete_url'),
    path('links/<int:pk>/toggle/', views.toggle_url, name='toggle_url'),
    path('links/<int:pk>/qr/', views.generate_qr, name='generate_qr'),
    path('links/<int:pk>/qr-preview/', views.qr_preview, name='qr_preview'),
    path('<str:short_code>/', views.redirect_url, name='redirect_url'),
]
