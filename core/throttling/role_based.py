from rest_framework.throttling import UserRateThrottle

class UserRoleRateThrottle(UserRateThrottle):
    THROTTLE_RATES = {
        'anon': '1000/day',
        'Learner': '10000/day',
        'Teacher': '20000/day',
        'Admin': '50000/day',
    }
    
    def get_cache_key(self, request, view):
        # Set the request on the instance so that get_rate() can access it.
        self.request = request
        role = request.user.role if request.user.is_authenticated else 'anon'
        return f'throttle_{role}_{self.scope}'
    
    def get_rate(self):
        # If for any reason self.request is not set, default to 'anon'
        if not hasattr(self, 'request') or self.request is None:
            role = 'anon'
        else:
            role = self.request.user.role if self.request.user.is_authenticated else 'anon'
        return self.THROTTLE_RATES.get(role)