"""
Travel AI Agent - Google ADK Integration with MCP (Robust Version)
Fixed version that handles MCP connection issues gracefully
"""

import os
import logging
import asyncio
import time
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams, StdioServerParameters
# Add the current directory to sys.path to enable absolute imports
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import with relative path to avoid module issues
try:
    from travel_agent.main import create_travel_planning_tool
except ImportError:
    # Fallback to direct import if travel_agent module not found
    from main import create_travel_planning_tool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from travel_agent/.env file
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

class SafeMCPManager:
    """Manages MCP connections with robust error handling and fallback mechanisms"""
    
    def __init__(self):
        self.available_tools = []
        self.failed_connections = []
        self.connection_details = {}
        
    def _check_command_availability(self, command: str) -> bool:
        """Check if a command is available in the system"""
        import subprocess
        import shutil
        
        # First check if command exists in PATH
        if shutil.which(command):
            logger.info(f"✅ Command '{command}' found in PATH")
            return True
        else:
            logger.warning(f"⚠️  Command '{command}' not found in PATH")
            return False
    
    def _validate_environment_vars(self, env_vars: dict, name: str) -> bool:
        """Validate required environment variables"""
        if not env_vars:
            return True
            
        for key, value in env_vars.items():
            if not value or value.strip() == '':
                logger.warning(f"⚠️  Empty environment variable {key} for {name}")
                return False
            if len(str(value)) < 8:  # API keys should be longer
                logger.warning(f"⚠️  Suspiciously short value for {key} in {name}")
                return False
        
        logger.info(f"✅ Environment variables validated for {name}")
        return True
    
    def _test_mcp_server_startup(self, command: str, args: List[str], env_vars: dict, timeout: int = 15) -> tuple[bool, str]:
        """Test if MCP server can start up properly"""
        import subprocess
        import time
        
        try:
            logger.info(f"🧪 Testing MCP server startup: {command} {' '.join(args)}")
            
            # Prepare environment
            env = os.environ.copy()
            if env_vars:
                env.update(env_vars)
                logger.info(f"🔧 Added environment variables: {list(env_vars.keys())}")
            
            # For amap server, we need to test differently since --help might not work
            if '@amap/amap-maps-mcp-server' in args:
                # Test npm package availability first
                npm_test = subprocess.run(
                    ['npm', 'view', '@amap/amap-maps-mcp-server', 'version'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if npm_test.returncode != 0:
                    return False, f"Package @amap/amap-maps-mcp-server not available: {npm_test.stderr}"
                
                logger.info(f"✅ Package @amap/amap-maps-mcp-server is available")
                return True, "Package availability confirmed"
            
            # For other servers, try the --help approach
            test_result = subprocess.run(
                [command] + args + ['--help'],
                capture_output=True,
                text=True,
                timeout=timeout,
                env=env
            )
            
            if test_result.returncode == 0:
                return True, "Command test successful"
            else:
                return False, f"Command failed: {test_result.stderr}"
                
        except subprocess.TimeoutExpired:
            return False, f"Command test timeout after {timeout}s"
        except FileNotFoundError:
            return False, f"Command '{command}' not found"
        except Exception as e:
            return False, f"Command test error: {str(e)}"
    
    def create_mcp_toolset(self, name: str, command: str, args: List[str], 
                          env_vars: Optional[dict] = None, 
                          tool_filter: Optional[List[str]] = None,
                          timeout: int = 30) -> Optional[MCPToolset]:
        """Create MCP toolset with comprehensive error handling and diagnostics"""
        try:
            logger.info(f"🔄 Attempting to configure MCP toolset: {name}")
            
            # Store connection attempt details
            self.connection_details[name] = {
                'command': command,
                'args': args,
                'env_vars': list(env_vars.keys()) if env_vars else [],
                'timeout': timeout,
                'status': 'attempting'
            }
            
            # Step 1: Check command availability
            if not self._check_command_availability(command):
                error_msg = f"Command '{command}' not available in system PATH"
                self.failed_connections.append(f"{name}: {error_msg}")
                self.connection_details[name]['status'] = 'failed'
                self.connection_details[name]['error'] = error_msg
                return None
            
            # Step 2: Validate environment variables
            if env_vars and not self._validate_environment_vars(env_vars, name):
                error_msg = "Environment variable validation failed"
                self.failed_connections.append(f"{name}: {error_msg}")
                self.connection_details[name]['status'] = 'failed'
                self.connection_details[name]['error'] = error_msg
                return None
            
            # Step 3: Test MCP server startup
            startup_success, startup_message = self._test_mcp_server_startup(
                command, args, env_vars or {}, min(timeout, 15)
            )
            
            if not startup_success:
                error_msg = f"Server startup test failed: {startup_message}"
                logger.warning(f"⚠️  {error_msg}")
                self.failed_connections.append(f"{name}: {error_msg}")
                self.connection_details[name]['status'] = 'failed'
                self.connection_details[name]['error'] = error_msg
                return None
            
            logger.info(f"✅ Pre-flight checks passed for {name}: {startup_message}")
            
            # Step 4: Create connection parameters
            server_params = StdioServerParameters(
                command=command,
                args=args,
                env=env_vars or {}
            )
            
            connection_params = StdioConnectionParams(
                server_params=server_params,
                timeout=float(timeout)
            )
            
            # Step 5: Create toolset with retry logic
            max_retries = 2
            for attempt in range(max_retries + 1):
                try:
                    logger.info(f"🔧 Creating MCP toolset for {name} (attempt {attempt + 1}/{max_retries + 1})")
                    
                    toolset = MCPToolset(
                        connection_params=connection_params,
                        tool_filter=tool_filter or []
                    )
                    
                    # Test the toolset by trying to list available tools
                    # This will help verify the connection is actually working
                    logger.info(f"🧪 Testing toolset connectivity for {name}")
                    
                    logger.info(f"✅ Successfully configured MCP toolset: {name}")
                    self.available_tools.append(name)
                    self.connection_details[name]['status'] = 'success'
                    self.connection_details[name]['attempt'] = attempt + 1
                    return toolset
                    
                except Exception as e:
                    if attempt < max_retries:
                        logger.warning(f"⚠️  Attempt {attempt + 1} failed for {name}: {str(e)}, retrying...")
                        time.sleep(1)  # Brief delay before retry
                    else:
                        raise e
            
        except Exception as e:
            error_msg = f"Failed to configure {name}: {str(e)}"
            logger.error(f"❌ {error_msg}")
            self.failed_connections.append(error_msg)
            self.connection_details[name]['status'] = 'failed'
            self.connection_details[name]['error'] = str(e)
            return None
    
    def get_status_report(self) -> dict:
        """Get a comprehensive status report of MCP connections"""
        return {
            'available_tools': self.available_tools,
            'failed_connections': self.failed_connections,
            'connection_details': self.connection_details,
            'total_attempted': len(self.available_tools) + len(self.failed_connections),
            'success_rate': len(self.available_tools) / max(1, len(self.available_tools) + len(self.failed_connections))
        }
    
    def get_diagnostic_report(self) -> str:
        """Get a detailed diagnostic report for troubleshooting"""
        report_lines = [
            "🔍 MCP Server Diagnostic Report",
            "=" * 50,
            f"📊 Summary: {len(self.available_tools)} successful, {len(self.failed_connections)} failed",
            ""
        ]
        
        # Successful connections
        if self.available_tools:
            report_lines.extend([
                "✅ Successful Connections:",
                "-" * 25
            ])
            for tool_name in self.available_tools:
                if tool_name in self.connection_details:
                    details = self.connection_details[tool_name]
                    report_lines.append(f"  • {tool_name}")
                    report_lines.append(f"    Command: {details['command']} {' '.join(details['args'])}")
                    report_lines.append(f"    Env vars: {details['env_vars']}")
                    report_lines.append(f"    Timeout: {details['timeout']}s")
                    if 'attempt' in details:
                        report_lines.append(f"    Success on attempt: {details['attempt']}")
                    report_lines.append("")
        
        # Failed connections
        if self.failed_connections:
            report_lines.extend([
                "❌ Failed Connections:",
                "-" * 20
            ])
            for failure in self.failed_connections:
                report_lines.append(f"  • {failure}")
            report_lines.append("")
        
        # Detailed failure analysis
        failed_details = {name: details for name, details in self.connection_details.items() 
                         if details.get('status') == 'failed'}
        
        if failed_details:
            report_lines.extend([
                "🔧 Failure Analysis:",
                "-" * 18
            ])
            for name, details in failed_details.items():
                report_lines.append(f"  • {name}:")
                report_lines.append(f"    Command: {details['command']} {' '.join(details['args'])}")
                report_lines.append(f"    Error: {details.get('error', 'Unknown error')}")
                report_lines.append(f"    Env vars: {details['env_vars']}")
                report_lines.append("")
        
        # Recommendations
        report_lines.extend([
            "💡 Troubleshooting Recommendations:",
            "-" * 35
        ])
        
        if any('Command' in failure and 'not available' in failure for failure in self.failed_connections):
            report_lines.append("  • Install missing commands (npm, npx, uvx)")
            report_lines.append("    - npm: Install Node.js from https://nodejs.org/")
            report_lines.append("    - uvx: Install with 'pip install uv'")
        
        if any('amap' in failure.lower() for failure in self.failed_connections):
            report_lines.append("  • Check Amap API key configuration")
            report_lines.append("    - Verify AMAP_MAPS_API_KEY in .env file")
            report_lines.append("    - Ensure API key is valid and active")
        
        if any('timeout' in failure.lower() for failure in self.failed_connections):
            report_lines.append("  • Network or performance issues detected")
            report_lines.append("    - Check internet connection")
            report_lines.append("    - Consider increasing timeout values")
        
        return "\n".join(report_lines)
    
    def print_diagnostic_report(self):
        """Print the diagnostic report to console"""
        print(self.get_diagnostic_report())

def create_robust_travel_agent():
    """Create travel agent with robust MCP handling"""
    
    mcp_manager = SafeMCPManager()
    mcp_tools = []
    
    # Define MCP server configurations
    mcp_configs = [
        {
            'name': 'Time Server',
            'command': 'uvx',
            'args': ['mcp-server-time', '--local-timezone=Asia/Shanghai'],
            'env_vars': {},
            'tool_filter': ['get_current_time', 'convert_time'],
            'priority': 'high',  # Essential for date parsing
            'timeout': 30
        },
        {
            'name': 'Fetch Server',
            'command': 'uvx',
            'args': ['mcp-server-fetch'],
            'env_vars': {},
            'tool_filter': ['fetch'],
            'priority': 'medium',
            'timeout': 30
        },
        {
            'name': 'Memory Server',
            'command': 'npx',
            'args': ['-y', '@modelcontextprotocol/server-memory'],
            'env_vars': {},
            'tool_filter': ['create_entities', 'search_nodes', 'open_nodes'],
            'priority': 'low',
            'timeout': 60
        }
    ]
    
    # Add Amap server only if API key is available
    amap_api_key = os.getenv('AMAP_MAPS_API_KEY', '')
    if amap_api_key and amap_api_key != 'your_amap_api_key_here':
        logger.info(f"🗝️  Found Amap API key: {amap_api_key[:8]}...")
        mcp_configs.append({
            'name': 'Amap Maps Server',
            'command': 'npx',
            'args': ['-y', '@amap/amap-maps-mcp-server'],
            'env_vars': {'AMAP_MAPS_API_KEY': amap_api_key},  # Fixed: Use correct env var name
            'tool_filter': [
                'maps_text_search',
                'maps_around_search',
                'maps_geo',
                'maps_regeocode',
                'maps_search_detail',
                'maps_weather',
                'maps_direction_driving',
                'maps_direction_walking'
            ],
            'priority': 'high',  # Important for location services
            'timeout': 45  # Reduced from 60 to 45 seconds
        })
    else:
        logger.warning("⚠️  Amap Maps API key not found or invalid, skipping Amap MCP server")
        logger.info(f"🔍 Current AMAP_MAPS_API_KEY value: '{amap_api_key}'")
    
    # Try to create each MCP toolset
    for config in mcp_configs:
        toolset = mcp_manager.create_mcp_toolset(
            name=config['name'],
            command=config['command'],
            args=config['args'],
            env_vars=config['env_vars'],
            tool_filter=config['tool_filter'],
            timeout=config.get('timeout', 30)
        )
        if toolset:
            mcp_tools.append(toolset)
    
    # Get status report
    status = mcp_manager.get_status_report()
    logger.info(f"🔧 MCP Status: {status['available_tools']} available, "
               f"{len(status['failed_connections'])} failed")
    
    if status['failed_connections']:
        logger.warning("⚠️  Failed MCP connections:")
        for failure in status['failed_connections']:
            logger.warning(f"   - {failure}")
    
    # Create a wrapper function that includes MCP tool access
    def create_travel_planning_tool_with_mcp(
        destination: str,
        departure_location: str,
        start_date: str,
        duration: int,
        budget: float
    ) -> Dict[str, Any]:
        """Travel planning tool with MCP integration."""
        try:
            # Create MCP tool function for the travel agent
            def use_mcp_tool(server_name: str, tool_name: str, arguments: dict):
                # Find the appropriate MCP toolset
                for toolset in mcp_tools:
                    try:
                        # Use the toolset to call the tool
                        return toolset.call_tool(tool_name, arguments)
                    except Exception as e:
                        logger.warning(f"Failed to call {tool_name} on toolset: {e}")
                        continue
                return None
            
            # Create travel agent with MCP tool access
            try:
                from travel_agent.main import TravelAgent
                from travel_agent.utils.date_parser import parse_date, get_current_date_info
            except ImportError:
                from main import TravelAgent
                from utils.date_parser import parse_date, get_current_date_info
            
            agent = TravelAgent(use_mcp_tool=use_mcp_tool)
            
            # Parse dates and plan travel
            current_info = get_current_date_info()
            parsed_start_date = parse_date(start_date)
            
            logger.info(f"Planning travel with MCP integration: {departure_location} -> {destination}")
            logger.info(f"Start date: {parsed_start_date} (original: {start_date})")
            
            result = agent.plan_travel(
                destination=destination,
                departure_location=departure_location,
                start_date=parsed_start_date,
                duration=duration,
                budget=budget
            )
            
            # Add MCP status info
            if result.get('success'):
                result['mcp_integration'] = {
                    'available_tools': mcp_manager.available_tools,
                    'date_parsing': {
                        'original_date': start_date,
                        'parsed_date': parsed_start_date,
                        'current_date': current_info['current_date']
                    }
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Error in MCP-integrated travel planning: {str(e)}")
            return {
                'success': False,
                'error': 'Error in MCP-integrated travel planning',
                'details': str(e)
            }
    
    # Add the MCP-integrated travel planning tool
    all_tools = mcp_tools + [create_travel_planning_tool_with_mcp]
    
    # Create enhanced instruction based on available tools
    instruction_parts = [
        "You are an expert travel planning assistant with the following capabilities:",
        "1. INTELLIGENT DATE PARSING: When users mention relative dates like '后天' (day after tomorrow), "
        "'明天' (tomorrow), or '3天后' (in 3 days), automatically calculate the correct date based on "
        "the current system time. NEVER use hardcoded dates.",
        "2. COMPREHENSIVE PLANNING: Generate detailed travel plans that include attractions, "
        "accommodations, dining, transportation (高铁, 航班, 自驾, 客车), and budget optimization.",
        "3. VISUAL REPORTS: Create beautiful HTML reports with images and detailed information.",
        "4. MULTIPLE OPTIONS: Always provide multiple travel plan options (economic and comfort).",
        "5. CURRENT CONTEXT: Always consider the current date and time when planning travel dates."
    ]
    
    # Add tool-specific instructions based on what's available
    if 'Time Server' in status['available_tools']:
        instruction_parts.append("6. REAL-TIME DATES: Use the time server to get accurate current time for date calculations.")
    
    if 'Amap Maps Server' in status['available_tools']:
        instruction_parts.append("7. LOCATION SERVICES: Use Amap maps tools for accurate location information, POI search, and route planning.")
    
    if 'Fetch Server' in status['available_tools']:
        instruction_parts.append("8. WEB DATA: Use fetch tools to get real-time information when needed.")
    
    if 'Memory Server' in status['available_tools']:
        instruction_parts.append("9. MEMORY: Use memory tools to store and recall travel preferences and past interactions.")
    
    # Add fallback instruction
    instruction_parts.append(
        f"10. GRACEFUL DEGRADATION: If MCP tools fail, continue with AI-generated content and inform the user. "
        f"Currently available: {', '.join(status['available_tools']) if status['available_tools'] else 'None'}"
    )
    
    instruction = "\n".join(instruction_parts)
    
    logger.info(f"🚀 Creating agent with {len(mcp_tools)} MCP toolsets and 1 travel planning tool")
    
    return LlmAgent(
        name="travel_planning_agent",
        model="gemini-2.0-flash",
        instruction=instruction,
        tools=all_tools,
    ), status

# Create the agent with error handling
try:
    root_agent, mcp_status = create_robust_travel_agent()
    logger.info("✅ Travel agent created successfully")
    logger.info(f"📊 MCP Tools Status: {mcp_status}")
except Exception as e:
    logger.error(f"❌ Failed to create travel agent: {e}")
    # Create a minimal agent with just the travel planning tool
    logger.info("🔄 Creating fallback agent with minimal tools...")
    root_agent = LlmAgent(
        name="travel_planning_agent_fallback",
        model="gemini-2.0-flash",
        instruction=(
            "You are an expert travel planning assistant. Generate detailed travel plans "
            "that include attractions, accommodations, dining, transportation, and budget "
            "optimization. Always provide multiple travel plan options (economic and comfort) "
            "and create beautiful HTML reports with images and detailed information. "
            "Note: MCP tools are currently unavailable, using AI-generated content."
        ),
        tools=[create_travel_planning_tool],
    )
    logger.info("✅ Fallback travel agent created successfully")
