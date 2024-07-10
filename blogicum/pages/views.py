from django.shortcuts import render
from django.views.generic import TemplateView


class AboutTemplateView(TemplateView):
    """Выводит страницу с информацией о проекте."""

    template_name = 'pages/about.html'


class RulesTemplateView(TemplateView):
    """Выводит страницу с правилами проекта."""

    template_name = 'pages/rules.html'


def page_not_found(request, exception):
    return render(request, 'pages/404.html', status=404)


def csrf_failure(request, reason=''):
    return render(request, 'pages/403csrf.html', status=403)


def server_failure(request):
    return render(request, 'pages/500.html', status=500)
