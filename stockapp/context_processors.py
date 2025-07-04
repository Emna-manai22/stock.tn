def user_role(request):
    role = None
    user = request.user
    if user.is_authenticated:
        if user.is_superuser:
            role = 'admin'
        elif user.is_staff:
            role = 'staff'
        else:
            role = 'user'
    return {'user_role': role}
