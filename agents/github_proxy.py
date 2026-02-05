import requests
import datetime
import os

def check_github_activity(username="Ayoub"): # Default, or can be passed
    """Checks for public events on GitHub for the user in the last 12 hours.
    
    Returns:
        bool: True if coding activity found, False otherwise.
        str: Summary of activity.
    """
    url = f"https://api.github.com/users/{username}/events/public"
    print(f"--- 🐙 GITHUB PROXY: Scaning timeline for {username} ---")
    
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return False, f"Error reaching GitHub API: {response.status_code}"
            
        events = response.json()
        if not events:
            return False, "No recent public events found."
            
        # Check timestamps (UTC)
        now = datetime.datetime.utcnow()
        twelve_hours_ago = now - datetime.timedelta(hours=12)
        
        found_commits = False
        details = []
        
        for event in events:
            # Parse event time
            created_at = datetime.datetime.strptime(event['created_at'], "%Y-%m-%dT%H:%M:%SZ")
            
            if created_at > twelve_hours_ago:
                if event['type'] == 'PushEvent':
                    found_commits = True
                    repo = event['repo']['name']
                    count = len(event['payload'].get('commits', []))
                    details.append(f"Pushed {count} commits to {repo}")
                elif event['type'] == 'PullRequestEvent':
                    found_commits = True
                    details.append(f"PR Activity in {event['repo']['name']}")
        
        if found_commits:
            summary = "; ".join(details)
            return True, summary
        else:
            return False, "No coding events in the last 12 hours."
            
    except Exception as e:
        return False, f"GitHub Proxy Error: {e}"

if __name__ == "__main__":
    # Test
    status, msg = check_github_activity("google") # Test with a known active user or Ayoub
    print(f"Status: {status}, Msg: {msg}")
