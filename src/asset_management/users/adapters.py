from allauth.account.adapter import DefaultAccountAdapter


class CustomAccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        user = super().save_user(request, user, form, commit=False)
        data = form.cleaned_data
        user.role = data.get("role", "researcher")
        user.department = data.get("department", None)
        user.phone = data.get("phone", "")
        user.is_approved = False  # New users need approval
        if commit:
            user.save()
        return user
