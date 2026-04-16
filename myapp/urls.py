from django.urls import path
from . import views

urlpatterns=[
    path('',views.home,name='home'),
    path('login/',views.login_view,name='login'),
    path('register/',views.register,name='register'),
    path('logout/',views.log_out,name='logout'),
    path('librarian/',views.Admin,name='admin'),
    path('user/',views.user_view,name='user'),
    path('del/<int:id>',views.delete_book,name='deletebook'),
    path('return/<int:id>',views.return_book,name='return'),
    path('addbook/',views.add_books,name='addbook'),
    path('edit/<int:id>',views.book_edit,name='editbook'),
    path('borrow/<int:id>',views.borrow_book,name='borrowbook'),
    path('update_issue_date/<int:id>',views.issue_date,name='update_issue'),
    path('aprrove/<int:id>',views.aprrove_request,name='approve'),
    path('approveb/<int:id>',views.approve_borrow_request,name='approveborrow'),
]