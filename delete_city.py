"""
Simple script to delete a city and all its associated data from the database.
Run this before re-importing data to start fresh.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from database.db_manager import db_manager
from database.models import City

def delete_city(city_name: str):
    """
    Delete a city and all its associated data.
    
    Args:
        city_name: Name of city to delete (e.g., 'cleveland')
    """
    # Initialize database connection
    db_manager.initialize()
    
    with db_manager.get_session() as session:
        # Find the city
        city = session.query(City).filter(City.city_name == city_name).first()
        
        if not city:
            print(f"❌ City '{city_name}' not found in database.")
            print("\nAvailable cities:")
            all_cities = session.query(City).all()
            for c in all_cities:
                print(f"  - {c.city_name} ({c.display_name})")
            return False
        
        print(f"\n⚠️  WARNING: About to delete city '{city.display_name}' and ALL associated data:")
        print(f"   - City ID: {city.city_id}")
        print(f"   - This will delete:")
        print(f"     ✗ All parcels")
        print(f"     ✗ All target owners")
        print(f"     ✗ All import history")
        print(f"     ✗ All configurations")
        
        # Confirm deletion
        response = input(f"\nType 'DELETE {city_name.upper()}' to confirm: ")
        
        if response != f'DELETE {city_name.upper()}':
            print("\n❌ Deletion cancelled.")
            return False
        
        # Delete the city (CASCADE will delete all related data)
        city_display = city.display_name
        session.delete(city)
        session.commit()
        
        print(f"\n✅ Successfully deleted '{city_display}' and all associated data!")
        print("   You can now re-import this city with fresh data.")
        
        return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python delete_city.py <city_name>")
        print("\nExample:")
        print("  python delete_city.py cleveland")
        sys.exit(1)
    
    city_name = sys.argv[1]
    delete_city(city_name)

