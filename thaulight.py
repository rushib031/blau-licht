from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
import re
from threading import Thread
from queue import Queue
import time

app = Flask(__name__)

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
            # Format name for common Instagram username patterns
            formatted_names = [
                name.lower().replace(' ', ''),  # johnsmith
                name.lower().replace(' ', '.'),  # john.smith
                name.lower().replace(' ', '_'),  # john_smith
                f"real{name.lower().replace(' ', '')}"  # realjohnsmith
            ]
            
            results = []
            for username in formatted_names:
                results.append({
                    'possible_username': username,
                    'profile_url': f"https://instagram.com/{username}",
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
            # Format name for common Twitter username patterns
            formatted_names = [
                name.lower().replace(' ', ''),  # johnsmith
                name.lower().replace(' ', '_'),  # john_smith
                f"_{name.lower().replace(' ', '_')}_",  # _john_smith_
                f"real{name.lower().replace(' ', '')}"  # realjohnsmith
            ]
            
            results = []
            for username in formatted_names:
                results.append({
                    'possible_username': username,
                    'profile_url': f"https://twitter.com/{username}",
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
            # Format name for common Snapchat username patterns
            formatted_names = [
                name.lower().replace(' ', ''),  # johnsmith
                name.lower().replace(' ', '_'),  # john_smith
                f"{name.lower().replace(' ', '')}snap",  # johnsmithsnap
                f"snap_{name.lower().replace(' ', '_')}"  # snap_john_smith
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

        # Create threads for all search functions
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
            key, value = results_queue.put_nowait((platform, result))
            results[key] = value
            
        return results

@app.route('/')
def index():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Person Intelligence Gathering</title>
        <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    </head>
    <body class="bg-gray-100 min-h-screen p-8">
        <div class="max-w-4xl mx-auto">
            <h1 class="text-3xl font-bold mb-8 text-center text-gray-800">Person Intelligence Gathering</h1>
            <form action="/search" method="POST" class="mb-8">
                <div class="flex gap-4">
                    <input type="text" name="name" placeholder="Enter person's name" 
                           class="flex-1 p-2 border rounded shadow-sm">
                    <button type="submit" 
                            class="bg-blue-500 text-white px-6 py-2 rounded hover:bg-blue-600">
                        Search
                    </button>
                </div>
            </form>
            <div id="results"></div>
        </div>
        
        <script>
            document.querySelector('form').addEventListener('submit', async (e) => {
                e.preventDefault();
                const name = document.querySelector('input[name="name"]').value;
                const results = document.getElementById('results');
                
                results.innerHTML = '<div class="text-center">Searching...</div>';
                
                try {
                    const response = await fetch('/search', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({name: name}),
                    });
                    
                    const data = await response.json();
                    
                    let html = '<div class="space-y-6">';
                    
                    // GitHub Results
                    if (data.github) {
                        html += `
                            <div class="bg-white p-6 rounded-lg shadow">
                                <h2 class="text-xl font-semibold mb-4">GitHub Profile</h2>
                                <div class="flex items-center gap-4">
                                    <img src="${data.github.avatar_url}" alt="GitHub avatar" 
                                         class="w-16 h-16 rounded-full">
                                    <div>
                                        <p>Username: ${data.github.username}</p>
                                        <a href="${data.github.profile_url}" target="_blank" 
                                           class="text-blue-500 hover:underline">
                                            View Profile
                                        </a>
                                    </div>
                                </div>
                            </div>
                        `;
                    }
                    
                    // LinkedIn Results
                    if (data.linkedin) {
                        html += `
                            <div class="bg-white p-6 rounded-lg shadow">
                                <h2 class="text-xl font-semibold mb-4">LinkedIn</h2>
                                <p>${data.linkedin.note}</p>
                                <a href="${data.linkedin.possible_profile}" target="_blank" 
                                   class="text-blue-500 hover:underline">
                                    Possible Profile Link
                                </a>
                            </div>
                        `;
                    }
                    
                    // Instagram Results
                    if (data.instagram) {
                        html += `
                            <div class="bg-white p-6 rounded-lg shadow">
                                <h2 class="text-xl font-semibold mb-4">Instagram</h2>
                                <p class="mb-4">${data.instagram.note}</p>
                                <div class="space-y-2">
                                    ${data.instagram.possible_profiles.map(profile => `
                                        <div>
                                            <a href="${profile.profile_url}" target="_blank" 
                                               class="text-blue-500 hover:underline">
                                                @${profile.possible_username}
                                            </a>
                                        </div>
                                    `).join('')}
                                </div>
                            </div>
                        `;
                    }
                    
                    // Twitter Results
                    if (data.twitter) {
                        html += `
                            <div class="bg-white p-6 rounded-lg shadow">
                                <h2 class="text-xl font-semibold mb-4">Twitter</h2>
                                <p class="mb-4">${data.twitter.note}</p>
                                <div class="space-y-2">
                                    ${data.twitter.possible_profiles.map(profile => `
                                        <div>
                                            <a href="${profile.profile_url}" target="_blank" 
                                               class="text-blue-500 hover:underline">
                                                @${profile.possible_username}
                                            </a>
                                        </div>
                                    `).join('')}
                                </div>
                            </div>
                        `;
                    }
                    
                    // Snapchat Results
                    if (data.snapchat) {
                        html += `
                            <div class="bg-white p-6 rounded-lg shadow">
                                <h2 class="text-xl font-semibold mb-4">Snapchat</h2>
                                <p class="mb-4">${data.snapchat.note}</p>
                                <div class="space-y-2">
                                    ${data.snapchat.possible_usernames.map(username => `
                                        <div>
                                            <a href="${data.snapchat.search_url}${username}" target="_blank" 
                                               class="text-blue-500 hover:underline">
                                                ${username}
                                            </a>
                                        </div>
                                    `).join('')}
                                </div>
                            </div>
                        `;
                    }
                    
                    // News Results
                    if (data.news && data.news.length > 0) {
                        html += `
                            <div class="bg-white p-6 rounded-lg shadow">
                                <h2 class="text-xl font-semibold mb-4">News Mentions</h2>
                                <ul class="space-y-2">
                                    ${data.news.map(article => `
                                        <li>
                                            <a href="${article.url}" target="_blank" 
                                               class="text-blue-500 hover:underline">
                                                ${article.title}
                                            </a>
                                        </li>
                                    `).join('')}
                                </ul>
                            </div>
                        `;
                    }
                    
                    html += '</div>';
                    results.innerHTML = html;
                    
                } catch (error) {
                    results.innerHTML = `
                        <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
                            Error: ${error.message}
                        </div>
                    `;
                }
            });
        </script>
    </body>
    </html>
    """

@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    name = data.get('name', '')
    
    if not name:
        return jsonify({'error': 'Name is required'}), 400
        
    intel = PersonIntel()
    results = intel.gather_all_info(name)
    
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)