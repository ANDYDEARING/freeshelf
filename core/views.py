from django.shortcuts import render
from django.views import generic
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import permission_required, login_required
from core.models import Book, Category, Favorite, Comment, BookSuggestion
from core.forms import FavoriteButtonForm, CommentCreateForm, BookForm, BookSuggestionForm, CategoryCreateForm


class BookListView(generic.ListView):
    model = Book

def all_books(request):
    sort_types = ['added_at', 'author', 'title',]
    
    sort_by = request.GET.get('sort_by', default='added_at')
    if sort_by not in sort_types:
        sort_by = 'added_at'

    category_list = Category.objects.all()
    book_list = Book.objects.all().order_by(sort_by)
    
    return render(request, 'core/book_list.html', {
        'book_list': book_list,
        'sort_by': sort_by,
        'sort_types': sort_types,
        'category_list': category_list,
     })

def category_books(request, pk):
    sort_types = ['added_at', 'author', 'title',]
    chosen_category = Category.objects.filter(id=pk).first()
    sort_by = request.GET.get('sort_by', default='added_at')
    if sort_by not in sort_types:
        sort_by = 'added_at'

    category_list = Category.objects.all()
    book_list = Book.objects.filter(category__id=pk).order_by(sort_by)

    return render(request, 'core/category_list.html', {
        'book_list': book_list,
        'sort_by': sort_by,
        'sort_types': sort_types,
        'chosen_category': chosen_category,
        'category_list': category_list,
     })

@login_required
def favorites(request,pk):
    sort_types = ['favorited_at','added_at', 'author', 'title',]
    user_name = User.objects.get(id=pk).username
    sort_by = request.GET.get('sort_by', default='favorited_at')
    if sort_by not in sort_types:
        sort_by = 'favorited_at'
    book_list = []
    fave_list = request.user.favorite_set.all().order_by('-favorited_at')
    for favorite in fave_list:
        book_list.append(favorite.favorite_book)

    # AREA FOR IMPROVEMENT book_list should be a QuerySet
    if sort_by == 'added_at':
        book_list.sort(key=lambda book:book.added_at)
    if sort_by == 'author':
        book_list.sort(key=lambda book:book.author)
    if sort_by == 'title':
        book_list.sort(key=lambda book:book.title)

    return render(request, 'core/favorites.html', {
        'user_name': user_name,
        'book_list': book_list,
        'sort_by': sort_by,
        'sort_types': sort_types,
     })

def book_detail(request,pk):
    if request.method == 'POST':
        form = FavoriteButtonForm(request.POST)
        if form.is_valid():
            favorited = form.cleaned_data['favorited']
            book = Book.objects.get(pk=pk)
            if favorited:
                new_fav = Favorite(user=request.user,favorite_book=book)
                book.times_favorited += 1
                book.save()
                new_fav.save()
            else:
                old_fav = Favorite.objects.filter(user=request.user).filter(favorite_book=book).first()
                book.times_favorited -= 1
                book.save()
                old_fav.delete()

        return redirect(to='book-detail', pk=pk)

    else:            
        form = FavoriteButtonForm()
        book = Book.objects.get(pk=pk)
        fave_list = book.favorite_set.all()
        favorite_users=[]
        for favorite in fave_list:
            favorite_users.append(favorite.user)
        comments = book.comment_set.all()
        # breakpoint()
        return render(request, 'core/book_detail.html', {
            'comments' : comments,
            'book' : book,
            'favorite_users' : favorite_users,
            'form' : form
        })

@login_required
def make_comment(request,pk):
    if request.method == 'POST':
        form = CommentCreateForm(request.POST)
        if form.is_valid():
            # breakpoint()
            content = form.cleaned_data['content']
            book = Book.objects.get(pk=pk)
            new_comment = Comment(user=request.user,content=content,target_book=book)
            new_comment.save()
        return redirect(to='book-detail', pk=pk)
    else:
        form = CommentCreateForm()
        book = Book.objects.get(pk=pk)

        return render(request, 'core/comment.html', {
            'book' : book,
            'form' : form,
        })

def user_profile(request,pk):
    user = User.objects.get(pk=pk)
    favorites = user.favorite_set.all()
    comments = user.comment_set.all()
    favorite_books=[]
    for favorite in favorites:
        favorite_books.append(favorite.favorite_book)
    # breakpoint()
    return render(request, 'core/user_profile.html', {
        'user' : user,
        'favorite_books' : favorite_books,
        'comments' : comments,
    })

@permission_required('core.can_add_edit_delete')
def staff_page(request):
    book_list = Book.objects.all()
    return render(request, 'core/staff.html', {
        'book_list' : book_list,
    })

@permission_required('core.can_add_edit_delete')
def edit_book(request,pk):
    book = Book.objects.get(pk=pk)
    categories = Category.objects.all()
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            book.title = form.cleaned_data['title']
            book.author = form.cleaned_data['author']
            book.url = form.cleaned_data['url']
            book.description = form.cleaned_data['description']
            book.image_url = form.cleaned_data['image_url']
            book.save()
            book.category.clear()
            # breakpoint()
            for category in form.cleaned_data['category']:
                book.category.add(category.id)
            book.save()
        return redirect(to='staff')
    else:
        form = BookForm()
    return render(request, 'core/edit_book.html', {
        'book' : book,
        'form' : form,
        'categories' : categories,
    })

@permission_required('core.can_add_edit_delete')
def delete_book(request,pk):
    book = Book.objects.get(pk=pk)
    book.delete()
    return redirect(to='staff')

@permission_required('core.can_add_edit_delete')
def add_book(request):
    new_book = Book()
    categories = Category.objects.all()
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            new_book.title = form.cleaned_data['title']
            new_book.author = form.cleaned_data['author']
            new_book.url = form.cleaned_data['url']
            new_book.description = form.cleaned_data['description']
            new_book.image_url = form.cleaned_data['image_url']
            new_book.save()
            for category in form.cleaned_data['category']:
                new_book.category.add(category.id)
            new_book.save()
        return redirect(to='staff')
    else:
        form = BookForm()
    return render(request, 'core/add_book.html', {
        'new_book' : new_book,
        'form' : form,
        'categories' : categories,
    })

@login_required
def suggestions(request):
    if request.method == 'POST':
        form = BookSuggestionForm(request.POST)
        # breakpoint()
        if form.is_valid():
            new_suggestion = BookSuggestion()
            new_suggestion.user = request.user
            new_suggestion.title = form.cleaned_data['title']
            new_suggestion.author = form.cleaned_data['author']
            new_suggestion.url = form.cleaned_data['url']
            new_suggestion.description = form.cleaned_data['description']
            new_suggestion.image_url = form.cleaned_data['image_url']
            new_suggestion.suggested_categories = form.cleaned_data['suggested_categories']
            new_suggestion.save()
        return redirect(to='suggestions')
    else:
        suggestions = BookSuggestion.objects.all()
        form = BookSuggestionForm()
        return render(request, 'core/suggestions.html', {
            'form' : form,
            'suggestions' : suggestions
        })

@permission_required('core.can_add_edit_delete')
def approve_suggestion(request,pk):
    suggestion = BookSuggestion.objects.get(pk=pk)
    categories = Category.objects.all()
    if request.method == 'POST':
        form = BookForm(request.POST)
        book = Book()
        if form.is_valid():
            book.title = form.cleaned_data['title']
            book.author = form.cleaned_data['author']
            book.url = form.cleaned_data['url']
            book.description = form.cleaned_data['description']
            book.image_url = form.cleaned_data['image_url']
            book.save()
            book.category.clear()
            for category in form.cleaned_data['category']:
                book.category.add(category.id)
            book.save()
            suggestion.delete()
        return redirect(to='suggestions')
    else:
        form = BookForm()
    return render(request, 'core/approve_suggestion.html', {
        'suggestion' : suggestion,
        'form' : form,
        'categories' : categories,
    })

@permission_required('core.can_add_edit_delete')
def delete_suggestion(request,pk):
    suggestion = BookSuggestion.objects.get(pk=pk)
    suggestion.delete()
    return redirect(to='suggestions')

@permission_required('core.can_add_edit_delete')
def delete_confirm(request,pk):
    book = Book.objects.get(pk=pk)
    return render(request, 'core/delete_confirm.html', {
        'book' : book,
    })

@permission_required('core.can_add_edit_delete')
def make_category(request):
    if request.method == 'POST':
        form = CategoryCreateForm(request.POST)
        if form.is_valid():
            new_category = Category()
            new_category.name = form.cleaned_data['category']
            new_category.save()
        return redirect(to='staff')
    else:
        form = CategoryCreateForm()
    return render(request, 'core/make_category.html', {
        'form' : form,
    })