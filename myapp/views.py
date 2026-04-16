from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Book, Issue, Fine,NewUser,Borrow_Request,Author
from datetime import datetime

def is_staff_user(user):
    return user.is_superuser

@login_required
def home(request):
    return render(request,'home.html')

@login_required
def log_out(request):
    logout(request)
    return redirect('login')

def update_book_details(request,bor):
    book=Book.objects.get(name=bor.book)
    user=bor.user
    issue=Issue.objects.create(user=user,book=book)
    issue.save()
    if book.no_books>=1:
        print("book no is greater than 1")
        book.no_books-=1
        book.save()
        messages.success(request,"Bookupdated")



def approve_borrow_request(request,id):
    data=Borrow_Request.objects.get(id=id)
    if data is not None:
        data.isapproved=True
        data.save()
        update_book_details(request,data)
    return redirect('admin')
        


@user_passes_test(is_staff_user)
def aprrove_request(request,id):
    nu=NewUser.objects.get(id=id)
    if nu is not None:
        nu.isapproved=True
        nu.save()
        return redirect('admin')
    else:
        messages.error(request,"error occured")
    return redirect('admin')


def login_view(request):
    if request.method=='POST':
        username=request.POST.get('username')
        password=request.POST.get('password')
        user=authenticate(request,username=username,password=password)
        if is_staff_user(user):
            if user is not None:
                login(request, user)
                return redirect('admin')
    

        if not NewUser.objects.get(user=user).isapproved:
            messages.error(request,"not approved by admin")
            return redirect('login')
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request,"Invalid credentials")
    return render(request,'login.html')



def register(request):
    if request.method=='POST':
        username=request.POST.get('username')
        password=request.POST.get('password')
        email=request.POST.get('email')
        if User.objects.filter(username=username).exists():
            messages.error(request,"Username already exists")
        elif User.objects.filter(email=email).exists():
            messages.error(request,"Email already exist")
        else:
            user=User.objects.create_user(username=username,password=password,email=email)
            nuser=NewUser.objects.create(user=user)
            nuser.save()
            user.save()
            messages.success(request,"User created succesfully")
            return redirect('login')
    return render(request,'register.html')


@user_passes_test(is_staff_user)
def delete_book(request,id):
    book=Book.objects.filter(id=id)
    book.delete()
    return redirect('admin')


@user_passes_test(is_staff_user)
def add_books(request):
    if request.method=='POST':
        name=request.POST.get('name')
        author=request.POST.get('author')
        isbn=request.POST.get('isbn')
        no_book=request.POST.get('no_books')
        print(name,author,isbn,no_book)
        if Book.objects.filter(isbn=isbn).exists():
            messages.error(request,"Book isbn already exist")
            print("Error occured")
            return redirect('admin')
        else:
            nauthor=Author.objects.create(name=author)
            book=Book.objects.create(name=name,author=nauthor,isbn=isbn,no_books=no_book)
            return redirect('admin')
    return render(request,'add_books.html')

@login_required
def return_book(request, id):
    issue = get_object_or_404(Issue, id=id, user=request.user)

    if issue.returned:
        messages.error(request, "Book already returned")
    else:
        book = issue.book
        book.no_books += 1
        book.save()
        issue.returned = True
        issue.returned_date=datetime.now()
        issue.save()
        messages.success(request, "Book returned successfully")
    return redirect('user')

@login_required
def issue_date(request,id):
    issue=Issue.objects.get(id=id)
    if request.method=='POST':
        return_date=request.POST.get('newdate')
        print(return_date)
        issue.returned_date=return_date
        issue.save()
        return redirect('admin')
    return render(request,'issue_date.html',{'returndate':issue.returned_date})



@login_required
def borrow_book(request, id):
    book = get_object_or_404(Book, id=id)
    borrow=Borrow_Request.objects.create(book=book,user=request.user)

    if book.no_books == 0:
        messages.error(request, "Book is not available")
    
    elif book.no_books > 0 and borrow.isapproved:
        Issue.objects.create(user=request.user, book=book)

        book.no_books -= 1
        book.save()

        messages.success(request, "Successfully borrowed book")
        return redirect('user')
    elif not borrow.isapproved:
        messages.error(request,"Not approved by amdin")
        return redirect('user')

    else:
        messages.error(request, "Error occurred")
    return redirect('user')



@login_required
def user_view(request):
    books = Book.objects.all()
    
    issued = Issue.objects.filter(user=request.user)
    
    if request.method == 'POST':
        bookname = request.POST.get('book')
        books = Book.objects.filter(name=bookname)
    
    return render(request, 'user.html', {'books': books, 'cr_user': request.user, 'issued': issued})

@user_passes_test(is_staff_user)
def book_edit(request, id):
    book = Book.objects.get(id=id)

    if request.method == 'POST':
        book.name = request.POST.get('name')
        book.author = request.POST.get('author')
        book.no_books = request.POST.get('no_books')

        book.save()
        return redirect('admin')

    return render(request, 'edit_books.html', {'book': book})

@user_passes_test(is_staff_user)
def Admin(request):
    books = Book.objects.all()
    user = User.objects.all()
    issue = Issue.objects.all()
    newuser = NewUser.objects.all()
    author = Author.objects.all()
    borrow = Borrow_Request.objects.all()
    
    if request.method == 'POST':
        print("Get inside the post")
        a = request.POST.get('drop1')
        print(a)
        if a is not None:
            print(a)
            c_a = Author.objects.get(id=a)
            books = Book.objects.filter(author=c_a)
        else:
            print("a is none")
    
    return render(request, 'Admin.html',
                  {'books': books,
                   'users': user,
                   'issued': issue,
                   'newuser': newuser,
                   'author': author,
                   'borrow': borrow,
                   })
