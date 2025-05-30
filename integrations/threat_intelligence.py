import requests


class ThreatIntelligence:
    API_URL = "https://threat-intelligence-api.example.com"

    @staticmethod
    def get_threat_data(ip):
        """Fetch threat intelligence data for a given IP address."""
        try:
            response = requests.get(
                f"{ThreatIntelligence.API_URL}/threats/{ip}", timeout=5
            )
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Failed to fetch data: {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
