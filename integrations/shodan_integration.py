"""
Shodan Integration Module
Author: morningstar
Poster: morningstar's Ethical Hacking Suite
Description: Integration with Shodan API for enhanced scanning and data
retrieval
"""

import shodan

API_KEY = "YOUR_SHODAN_API_KEY"  # Replace with your actual Shodan API key


class ShodanIntegration:
    def __init__(self):
        self.api = shodan.Shodan(API_KEY)

    def search_ip(self, ip):
        """Search for information about an IP address using Shodan."""
        try:
            result = self.api.host(ip)
            return result
        except shodan.APIError as e:
            return {"error": str(e)}

    def search_query(self, query):
        """Search Shodan with a custom query."""
        try:
            results = self.api.search(query)
            return results
        except shodan.APIError as e:
            return {"error": str(e)}
