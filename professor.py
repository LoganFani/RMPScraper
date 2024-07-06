import requests
import json
import os
import base64
import math
import re

current_path = os.path.dirname(__file__)

with open(os.path.join(current_path, "json/header.json"),'r') as f:
    headers = json.load(f)

with open(os.path.join(current_path, "json/profquery.json"),'r') as f:
    professor_query = json.load(f)

class Professor:
    def __init__(self, prof_name: str, university_id: int = 1162) -> None:
        
        self.university_id = university_id

        self.id = self.get_prof_id(prof_name)
        self.get_ratings(self.id)
    
    def get_ratings(self, prof_id: int) -> None:

        if self.id == 0:
            return
        
        headers['Referer'] = f"https://www.ratemyprofessors.com/ShowRatings.jsp?tid={prof_id}"
        professor_query["variables"]["id"] = base64.b64encode((f"Teacher-{prof_id}").encode('ascii')).decode('ascii')

        page_data = requests.post(url="https://www.ratemyprofessors.com/graphql", json=professor_query, headers=headers)

        if page_data is None or json.loads(page_data.text)["data"]["node"] is None:
            raise ValueError("Professor not found with that id or bad request.")
        
        professor_data = json.loads(page_data.text)["data"]["node"]

        self.name = professor_data["firstName"] + ' ' + professor_data["lastName"]
        self.department = professor_data["department"]
        self.difficulty = professor_data["avgDifficulty"]
        self.rating = professor_data["avgRating"]
        self.prof_url = f"https://www.ratemyprofessors.com/professor/{self.id}"

        if professor_data["wouldTakeAgainPercent"] == 0:
            self.would_take_again = None

        else:
            self.would_take_again = math.ceil(professor_data["wouldTakeAgainPercent"])
            self.num_ratings = professor_data["numRatings"]
    
    def get_prof_id(self, name: str) -> int:
        temp_list = []
        
        url = f'https://www.ratemyprofessors.com/search/professors/{self.university_id}?q={name}'
        page = requests.get(url)
        data = re.findall(r'"legacyId":(\d+)', page.text)

        if len(data) <1 :
            self.set_prof_not_found()
            return 0

        for prof_id in data:
            temp_list.append(int(prof_id))
        
        return temp_list[0]
    
    def set_prof_not_found(self) -> None:
        self.prof_url = "None"
        self.name = "Professor N/A"
        self.department = "None"
        self.difficulty = 0
        self.rating = 0
        self.would_take_again = 0
        self.num_ratings = 0


    def print_prof(self) -> None:
        print(f"{self.name}\n{self.department}\nDifficulty: {self.difficulty}\nRating: {self.rating}\nTake_Again: {self.would_take_again}\nNumber of Ratings: {self.num_ratings}")
        print(f"Prof_URL: {self.prof_url}")


