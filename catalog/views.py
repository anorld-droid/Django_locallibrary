import datetime
from django.http import request
from django.views import generic
from .models import Author, Book, Bookinstance, Genre
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse

from .forms import RenewBookForm


# Create your views here.


@login_required
# @permission_required('catalog.can_mark_returned', raise_exception=True)
def index(request):
    """View function for home page"""

    # Generate counts for some of the main objects
    num_books = Book.objects.all().count()
    num_instances = Bookinstance.objects.all().count()
    num_genres = Genre.objects.all().count()
    num_books_containing_the = Book.objects.filter(
        title__icontains='The').count()

    # Availble books (status = a)
    num_instances_available = Bookinstance.objects.filter(
        status__exact='a').count()

    # The 'all()' is implied by default
    num_authors = Author.objects.count()
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_genres': num_genres,
        'num_books_containing_the': num_books_containing_the,
        'num_visits': num_visits,
    }

    # Render the html index with the data in the context available
    return render(request, 'index.html', context=context)


class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 10


class AuthorDetailView(generic.DetailView):
    model = Author


class BookListView(generic.ListView):
    model = Book
    paginate_by = 10
    # context_object_name = 'my_book_list'   # your own name for the list as a template variable
    # queryset = Book.objects.filter(title__icontains='war')[:5] # Get 5 books containing the title war
    # template_name = 'books/my_arbitrary_template_name_list.html'  # Specify your own template name/location


class BookDetailView(generic.DetailView):
    model = Book


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic classed based view listing books on loan to current user"""
    model = Bookinstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return Bookinstance.objects.filter(borrower=self.request.user).filter(
            status__exact='o'
        ).order_by('due_back')


class LoanedBooksListViewForLibrarians(PermissionRequiredMixin, generic.ListView):
    """Generic class-based view listing all books on loan. Only visible to users with can_mark_returned permission."""
    model = Bookinstance
    permission_required = 'catalog.can_mark_returned'
    template_name = 'catalog/bookinstance_list_librarian.html'

    def get_queryset(self):
        return Bookinstance.objects.filter(status__exact='o').order_by('due_back')


@login_required
@permission_required('catalog.cn_mark_return', raise_exception=True)
def renew_book_librarian(request, pk):
    book_instance = get_object_or_404(Bookinstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('borrowed_books'))

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)
