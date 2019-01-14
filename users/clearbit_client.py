import clearbit
from django.conf import settings




class ClearbitClient:
    clearbit.key = settings.CLEARBIT_API_KEY

    @classmethod
    def get_person_data(cls, email):
        response = clearbit.Enrichment.find(email=email)
        result = {}
        if 'person' in response:
            person = response["person"]
            result["first_name"] = person.get("name", {}).get("givenName")
            result["last_name"] = person.get("name", {}).get("familyNameName")
            result["location"] = person.get("location")
            result["bio"] = person.get("bio")
            result["site"] = person.get("site")
            result["avatar"] = person.get("avatar")
            result["facebook"] = person.get("facebook", {}).get("handle")
            result["linkedin"] = person.get("facebook", {}).get("linkedin")
        return result

    @classmethod
    def update_person_data(cls, clearbit_data, person_data):

        result = person_data.copy()
        for key, value in clearbit_data.items():
            if not person_data.get(key) and value:
                result[key] = value
        return result

