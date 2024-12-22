import requests
import json
from datetime import datetime, timedelta

class BufferPostingAgent:
    def __init__(self, access_token):
        self.access_token = access_token
        self.base_url = "https://api.buffer.com/1"
        self.supported_services = {
            'twitter': 'x',      # X/Twitter
            'facebook': 'facebook',
            'linkedin': 'linkedin',
            'instagram': 'instagram',
            'bluesky': 'bluesky',
            'mastodon': 'mastodon'
        }
    
    def get_profiles_by_service(self, services=None):
        """
        Get profiles filtered by service type
        
        Args:
            services (list): List of service names (e.g., ['twitter', 'facebook'])
        Returns:
            dict: Profiles grouped by service
        """
        profiles = self.get_profiles()
        
        if not services:
            return profiles
            
        filtered_profiles = {}
        for profile in profiles:
            service = profile['service'].lower()
            if service in services:
                if service not in filtered_profiles:
                    filtered_profiles[service] = []
                filtered_profiles[service].append(profile)
                
        return filtered_profiles

    def create_targeted_post(self, content, services=None, scheduled_at=None):
        """
        Create posts targeting specific social media platforms
        
        Args:
            content (dict): Platform-specific content
            services (list): List of services to post to
            scheduled_at (datetime): Optional scheduling time
        """
        if not services:
            services = list(self.supported_services.keys())
            
        profiles = self.get_profiles_by_service(services)
        
        results = {}
        for service in services:
            if service not in profiles:
                results[service] = {"error": "No profile found"}
                continue
                
            # Get service-specific content or fall back to default
            post_content = content.get(service, content.get('default', ''))
            
            # Get profile IDs for this service
            profile_ids = [p['id'] for p in profiles[service]]
            
            # Create the post
            result = self.create_post(
                profile_ids=profile_ids,
                text=post_content,
                scheduled_at=scheduled_at
            )
            
            results[service] = result
            
        return results

def main():
    ACCESS_TOKEN = "your_access_token_here"
    agent = BufferPostingAgent(ACCESS_TOKEN)
    
    # Example: Platform-specific content
    content = {
        'default': "Check out our latest update! 🚀",
        'twitter': "New release! 🚀 #TechNews",
        'facebook': "We're excited to announce our latest update! Click below to learn more. 🚀",
        'linkedin': "Proud to announce our latest professional milestone. #Innovation #Technology",
        'bluesky': "Just shipped a new update! 🚀 #Tech"
    }
    
    # Post only to specific platforms
    selected_services = ['twitter', 'facebook', 'bluesky']
    
    # Create the posts
    results = agent.create_targeted_post(
        content=content,
        services=selected_services,
        scheduled_at=datetime.now() + timedelta(hours=1)
    )
    
    # Check results
    for service, result in results.items():
        print(f"\nResults for {service}:")
        print(result)

if __name__ == "__main__":
    main()