from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        if sociallogin.account.provider == 'google':
            user.photo = sociallogin.account.extra_data.get('picture')
            user.username = sociallogin.account.extra_data.get('email')
            user.first_name = sociallogin.account.extra_data.get('given_name')
            user.last_name = sociallogin.account.extra_data.get('family_name')
        
        if sociallogin.account.provider == 'vk':
            user.photo = sociallogin.account.extra_data.get('image')
            user.username = sociallogin.account.extra_data.get('email')
            user.first_name = sociallogin.account.extra_data.get('first_name')
            user.last_name = sociallogin.account.extra_data.get('last_name')

        user.save()
        return user