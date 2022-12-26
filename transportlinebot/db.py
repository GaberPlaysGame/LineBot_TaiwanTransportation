import json
import os

class MRT_Route_DB:

    def search(self, mode: int, text: str):
        if mode == 0:
            return self.search_taipei(text)   
        
    def search_taipei(self, text: str):
        f = open('./transportlinebot/json/route_mrt_taipei.json', encoding="utf-8")
        data = json.load(f)
        f.close()

        for i in data['data']:
            if text in i['alias']:
                return i
        return None
