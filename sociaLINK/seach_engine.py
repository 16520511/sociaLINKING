from .models import MyUser

class SearchEngine:
    def __init__(self):
        self.result = MyUser.objects.all()

    def search_by_name(self, query):
        if query == "" or query == None:
            return self
        emailMatch = self.result.filter(email__icontains = query)
        nameMatch = self.result.filter(firstName__icontains = query)|MyUser.objects.filter(lastName__icontains = query)
        self.result = (emailMatch|nameMatch).distinct()
        return self

    def search_by_location(self, query):
        if query == "" or query == None:
            return self
        locationMatch = self.result.filter(profile__location__icontains = query)
        self.result = locationMatch
        return self
