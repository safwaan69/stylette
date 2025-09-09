from .models import Category


def categories(request):
    """Context processor to make categories available in all templates"""
    return {
        'categories': Category.objects.all()[:6],  # Limit to 6 categories for navigation
    }


