#!/usr/bin/env python3
"""
Test script for Travel AI Agent
"""

import sys
import os
sys.path.append('travel_agent')

from travel_agent.main import TravelAgent

def test_travel_agent():
    """Test the Travel AI Agent with a sample request."""
    print("🚀 Testing Travel AI Agent...")
    print("=" * 50)
    
    try:
        # Initialize the agent
        agent = TravelAgent()
        print("✅ Travel Agent initialized successfully")
        
        # Test with sample data
        result = agent.plan_travel(
            destination="Tokyo, Japan",
            departure_location="Shanghai, China",
            start_date="2024-04-01",
            duration=7,
            budget=8000
        )
        
        print("\n📊 Planning Result:")
        print(f"Success: {result.get('success', False)}")
        
        if result.get('success'):
            print(f"✅ Plans generated: {result.get('plans_count', 0)}")
            print(f"📄 Report saved to: {result.get('file_path', 'N/A')}")
            print(f"💬 Message: {result.get('message', 'N/A')}")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
            if result.get('details'):
                print(f"Details: {result.get('details')}")
        
        return result.get('success', False)
        
    except Exception as e:
        print(f"❌ Test failed with exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Travel AI Agent Test Suite")
    print("Testing the complete travel planning pipeline...\n")
    
    success = test_travel_agent()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed! Travel AI Agent is working correctly.")
        print("\n📝 Next steps:")
        print("1. Check the generated HTML report in travel_agent/output/")
        print("2. Open the HTML file in a browser to view the travel plan")
        print("3. Customize the agent settings in travel_agent/main.py")
    else:
        print("⚠️  Tests failed. Please check the error messages above.")
        print("\n🔧 Troubleshooting:")
        print("1. Ensure all dependencies are installed: pip install -r requirements.txt")
        print("2. Check API keys in travel_agent/.env")
        print("3. Verify all Python modules are properly imported")
    
    print("\n🚀 Ready to use the Travel AI Agent!")
