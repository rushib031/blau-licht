import requests
from bs4 import BeautifulSoup
import re
from threading import Thread
from queue import Queue
import time

class PersonIntel:
    def __init__(self):
        self.results = {}
        
    def search_github(self, name):
        try:
            url = f"https://api.github.com/search/users?q={name}"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if data['total_count'] > 0:
                    user = data['items'][0]
                    return {
                        'username': user['login'],
                        'profile_url': user['html_url'],
                        'avatar_url': user['avatar_url']
                    }
        except Exception as e:
            print(f"GitHub search error: {e}")
        return None

    def search_linkedin(self, name):
        try:
            formatted_name = name.lower().replace(' ', '-')
            return {
                'possible_profile': f"https://www.linkedin.com/in/{formatted_name}",
                'note': 'Profile link is speculative, requires manual verification'
            }
        except Exception as e:
            print(f"LinkedIn search error: {e}")
        return None

    def search_instagram(self, name):
        try:
            formatted_names = [
                name.lower().replace(' ', ''),
                name.lower().replace(' ', '.'),
                name.lower().replace(' ', '_'),
                f"real{name.lower().replace(' ', '')}"
            ]
            
            results = []
            for username in formatted_names:
                results.append({
                    'possible_username': username,
                    'profile_url': f"https://instagram.com/{username}"
                })
            
            return {
                'possible_profiles': results,
                'note': 'Links are potential matches based on common username patterns'
            }
        except Exception as e:
            print(f"Instagram search error: {e}")
        return None

    def search_twitter(self, name):
        try:
            formatted_names = [
                name.lower().replace(' ', ''),
                name.lower().replace(' ', '_'),
                f"_{name.lower().replace(' ', '_')}_",
                f"real{name.lower().replace(' ', '')}"
            ]
            
            results = []
            for username in formatted_names:
                results.append({
                    'possible_username': username,
                    'profile_url': f"https://twitter.com/{username}"
                })
            
            return {
                'possible_profiles': results,
                'note': 'Links are potential matches based on common username patterns'
            }
        except Exception as e:
            print(f"Twitter search error: {e}")
        return None

    def search_snapchat(self, name):
        try:
            formatted_names = [
                name.lower().replace(' ', ''),
                name.lower().replace(' ', '_'),
                f"{name.lower().replace(' ', '')}snap",
                f"snap_{name.lower().replace(' ', '_')}"
            ]
            
            return {
                'possible_usernames': formatted_names,
                'search_url': "https://www.snapchat.com/add/",
                'note': 'These are potential usernames based on common patterns. Use Snapchat\'s "Add Friends" feature to check.'
            }
        except Exception as e:
            print(f"Snapchat search error: {e}")
        return None

    def search_news(self, name):
        try:
            news_articles = []
            news_articles.append({
                'title': f"Search results for {name}",
                'url': f"https://news.google.com/search?q={name.replace(' ', '+')}"
            })
            return news_articles
        except Exception as e:
            print(f"News search error: {e}")
        return []

    def gather_all_info(self, name):
        results_queue = Queue()
        
        def worker(search_func, platform):
            result = search_func(name)
            if result:
                results_queue.put((platform, result))

        threads = [
            Thread(target=worker, args=(self.search_github, 'github')),
            Thread(target=worker, args=(self.search_linkedin, 'linkedin')),
            Thread(target=worker, args=(self.search_instagram, 'instagram')),
            Thread(target=worker, args=(self.search_twitter, 'twitter')),
            Thread(target=worker, args=(self.search_snapchat, 'snapchat')),
            Thread(target=worker, args=(self.search_news, 'news'))
        ]
        
        for thread in threads:
            thread.start()
            
        for thread in threads:
            thread.join()
            
        results = {}
        while not results_queue.empty():
            platform, result = results_queue.get()
            results[platform] = result
            
        return results