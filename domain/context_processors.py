from .forms import SearchForm
from .models import Usuario
def search_form(request):
    return {'search_form': SearchForm()}

def search_form(request):
    user_session = Usuario.objects.get_user_from_request(request)
    return {'user_session': user_session}