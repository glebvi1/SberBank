from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic.list import ListView

from vip_users.forms import CategoryCreateForm
from vip_users.models import Category


@login_required
def create_category(request):
    if request.method == "POST":
        form = CategoryCreateForm(data=request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.user = request.user
            form.save()
            return HttpResponseRedirect(reverse("vip_users:all_categories"))
    else:
        form = CategoryCreateForm()

    context = {"form": form}

    return render(request, "vip_users/create_category.html", context)


@method_decorator(login_required, name="dispatch")
class CategoriesListView(ListView):
    template_name = "vip_users/all_categories.html"
    model = Category

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)
