from django.db import models
from django.contrib.auth.models import User
from datetime import date

class NewUser(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    isapproved=models.BooleanField(default=False)

class Author(models.Model):
    name=models.TextField(max_length=255)

class Book(models.Model):
    name = models.CharField(max_length=255)
    author = models.ForeignKey(Author,on_delete=models.CASCADE)
    isbn = models.BigIntegerField(unique=True)
    no_books = models.IntegerField(null=False, default=1)


    def __str__(self):
        return self.name

    def available_copies(self):
        issued_count = Issue.objects.filter(book=self, returned=False).count()
        return self.no_books - issued_count


class Issue(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    issue_date = models.DateField(auto_now_add=True)
    returned_date = models.DateField(null=True, blank=True)
    returned = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.book.name} - {self.user.username}"

    def days_borrowed(self):
        if self.returned_date:
            return (self.returned_date - self.issue_date).days
        return (date.today() - self.issue_date).days

    def fine_amount(self):
        days = self.days_borrowed()
        if days > 1:
            return days * 5
        return 0


class Fine(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid = models.BooleanField(default=False)
    created_date = models.DateField(auto_now_add=True)
    paid_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.amount} - {self.issue.user.username}"
    

class Borrow_Request(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    book=models.ForeignKey(Book,on_delete=models.CASCADE)
    isapproved=models.BooleanField(default=False)