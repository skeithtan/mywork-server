from rest_framework.response import Response


def group_required(*group_names):
    """Requires user membership in at least one of the groups passed in."""

    def decorator(function):
        def wrap(request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated:
                return Response({
                    'error': 'User must be authenticated.'
                })

            groups = list(group_names)
            if user.groups.filter(name__in=groups).exists() | user.is_superuser:
                return function(request, *args, **kwargs)

            return Response({
                'error': f'User must belong to one of the following groups: {groups}'
            })

        return wrap

    return decorator


def professors_only(function):
    return group_required('Professors')(function)


def students_only(function):
    return group_required('Students')(function)
