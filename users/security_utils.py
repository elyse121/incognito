# security_utils.py
import requests
from django.utils import timezone
from user_agents import parse  # Install with: pip install pyyaml ua-parser user-agents


def get_device_info(user_agent_string):
    """Extract device information from user agent"""
    try:
        user_agent = parse(user_agent_string)
        device_info = ""
        
        if user_agent.is_mobile:
            device_info += "Mobile "
        elif user_agent.is_tablet:
            device_info += "Tablet "
        elif user_agent.is_pc:
            device_info += "Desktop "
        elif user_agent.is_bot:
            device_info += "Bot "
            
        if user_agent.device.brand:
            device_info += f"{user_agent.device.brand} "
        if user_agent.device.model:
            device_info += f"{user_agent.device.model}"
            
        return device_info.strip() if device_info else "Unknown Device"
    except:
        return "Unknown Device"

def get_browser_info(user_agent_string):
    """Extract browser information from user agent"""
    try:
        user_agent = parse(user_agent_string)
        browser_info = f"{user_agent.browser.family} {user_agent.browser.version_string}"
        return browser_info if browser_info.strip() else "Unknown Browser"
    except:
        return "Unknown Browser"

def get_os_info(user_agent_string):
    """Extract OS information from user agent"""
    try:
        user_agent = parse(user_agent_string)
        os_info = f"{user_agent.os.family} {user_agent.os.version_string}"
        return os_info if os_info.strip() else "Unknown OS"
    except:
        return "Unknown OS"

def get_geolocation_data(ip_address):
    """Get approximate geolocation data for an IP address"""
    # Skip for localhost or private IPs
    if ip_address in ['127.0.0.1', 'localhost'] or ip_address.startswith(('192.168.', '10.', '172.')):
        return {}
    
    try:
        # Using ipapi.co (free tier available)
        response = requests.get(f"https://ipapi.co/{ip_address}/json/", timeout=3)
        if response.status_code == 200:
            data = response.json()
            return {
                'city': data.get('city', 'Unknown'),
                'region': data.get('region', 'Unknown'),
                'country': data.get('country_name', 'Unknown'),
                'org': data.get('org', 'Unknown')
            }
    except:
        pass
        
    return {}

def get_typical_login_time(user):
    """Get user's typical login time patterns (simplified)"""
    # In a real implementation, you would analyze login history
    return "Not enough data"  # Placeholder

def get_typical_device(user):
    """Get user's typical device patterns (simplified)"""
    # In a real implementation, you would analyze device history
    return "Not enough data"  # Placeholder