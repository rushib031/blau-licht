document.getElementById('searchForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const name = document.querySelector('input[name="name"]').value;
    const results = document.getElementById('results');
    
    results.innerHTML = '<div class="text-center">Searching...</div>';
    
    try {
        console.log('Searching for:', name);  // Debug log
        
        const response = await axios.post('/search', { name: name });
        console.log('Response received:', response.data);  // Debug log
        
        const data = response.data;
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
        
        // If no results found
        if (Object.keys(data).length === 0) {
            html += `
                <div class="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded">
                    No results found for "${name}".
                </div>
            `;
        }
        
        html += '</div>';
        results.innerHTML = html;
        
    } catch (error) {
        console.error('Error:', error);  // Debug log
        results.innerHTML = `
            <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
                Error: ${error.message}
            </div>
        `;
    }
});