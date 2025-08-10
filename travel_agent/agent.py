"""
Travel AI Agent - Google ADK Integration with MCP (Optimized Version)
Enhanced version with clean tool initialization and async MCP support
"""

import os
import logging
import asyncio
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
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
    try:
        # Fallback to direct import if travel_agent module not found
        from main import create_travel_planning_tool
    except ImportError:
        # Create a minimal fallback function
        def create_travel_planning_tool(destination: str, departure_location: str, start_date: str, duration: int, budget: float) -> dict:
            return {
                'success': False,
                'error': 'Travel planning tool not available - import error',
                'fallback': True
            }

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from travel_agent/.env file
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

@dataclass
class MCPServerConfig:
    """MCP服务器配置数据类"""
    name: str
    command: str
    args: List[str]
    env_vars: Dict[str, str]
    tool_filter: List[str]
    priority: str
    timeout: int
    required: bool = False

class MCPToolConfig:
    """MCP工具配置管理器"""
    
    @staticmethod
    def get_base_configs() -> List[MCPServerConfig]:
        """获取基础MCP服务器配置"""
        return [
            MCPServerConfig(
                name='Time Server',
                command='uvx',
                args=['mcp-server-time', '--local-timezone=Asia/Shanghai'],
                env_vars={},
                tool_filter=['get_current_time', 'convert_time'],
                priority='high',
                timeout=30,
                required=True  # 时间服务是必需的
            ),
            MCPServerConfig(
                name='Fetch Server',
                command='uvx',
                args=['mcp-server-fetch'],
                env_vars={},
                tool_filter=['fetch'],
                priority='medium',
                timeout=30,
                required=False
            ),
            MCPServerConfig(
                name='Memory Server',
                command='npx',
                args=['-y', '@modelcontextprotocol/server-memory'],
                env_vars={},
                tool_filter=['create_entities', 'search_nodes', 'open_nodes'],
                priority='low',
                timeout=60,
                required=False
            )
        ]
    
    @staticmethod
    def get_amap_config() -> Optional[MCPServerConfig]:
        """获取Amap配置（如果API密钥可用）"""
        amap_api_key = os.getenv('AMAP_MAPS_API_KEY', '')
        if amap_api_key and amap_api_key != 'your_amap_api_key_here':
            logger.info(f"🗝️  Found Amap API key: {amap_api_key[:8]}...")
            return MCPServerConfig(
                name='Amap Maps Server',
                command='npx',
                args=['-y', '@amap/amap-maps-mcp-server'],
                env_vars={'AMAP_MAPS_API_KEY': amap_api_key},
                tool_filter=[
                    'maps_text_search', 'maps_around_search', 'maps_geo',
                    'maps_regeocode', 'maps_search_detail', 'maps_weather',
                    'maps_direction_driving', 'maps_direction_walking'
                ],
                priority='high',
                timeout=45,
                required=False
            )
        else:
            logger.warning("⚠️  Amap Maps API key not found or invalid, skipping Amap MCP server")
            logger.info(f"🔍 Current AMAP_MAPS_API_KEY value: '{amap_api_key}'")
        return None

class MCPToolRegistry:
    """MCP工具注册表"""
    
    def __init__(self):
        self.tools_by_name = {}
        self.tools_by_server = {}
        self.toolsets = []
        self.initialization_status = {}
    
    async def register_toolsets_async(self, toolsets: List[MCPToolset]):
        """异步注册工具集"""
        for toolset in toolsets:
            try:
                self.toolsets.append(toolset)
                
                # 异步获取工具列表
                tools = await toolset.get_tools()
                server_name = self._identify_server_type(toolset)
                
                logger.info(f"📋 Registering {len(tools)} tools from {server_name}")
                
                for tool in tools:
                    self.tools_by_name[tool.name] = tool
                    
                    # 根据服务器类型分组
                    if server_name not in self.tools_by_server:
                        self.tools_by_server[server_name] = []
                    self.tools_by_server[server_name].append(tool)
                
                self.initialization_status[server_name] = {
                    'status': 'success',
                    'tool_count': len(tools),
                    'tools': [tool.name for tool in tools]
                }
                
            except Exception as e:
                server_name = self._identify_server_type(toolset)
                logger.error(f"❌ Failed to register tools from {server_name}: {str(e)}")
                self.initialization_status[server_name] = {
                    'status': 'failed',
                    'error': str(e),
                    'tool_count': 0
                }
    
    async def call_tool_async(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """异步调用MCP工具"""
        if tool_name in self.tools_by_name:
            tool = self.tools_by_name[tool_name]
            try:
                logger.info(f"🔧 Calling MCP tool: {tool_name} with args: {arguments}")
                result = await tool.run_async(args=arguments)
                logger.info(f"✅ MCP tool {tool_name} executed successfully")
                return {
                    'success': True,
                    'result': result,
                    'tool_name': tool_name,
                    'source': 'mcp_direct_call'
                }
            except Exception as e:
                logger.error(f"❌ MCP tool {tool_name} failed: {str(e)}")
                return {
                    'success': False,
                    'error': str(e),
                    'tool_name': tool_name,
                    'source': 'mcp_direct_call'
                }
        else:
            logger.warning(f"⚠️  Tool {tool_name} not found in registry")
            return {
                'success': False,
                'error': f'Tool {tool_name} not found',
                'available_tools': list(self.tools_by_name.keys()),
                'source': 'mcp_direct_call'
            }
    
    def _identify_server_type(self, toolset: MCPToolset) -> str:
        """识别服务器类型"""
        try:
            if hasattr(toolset, '_connection_params'):
                server_params = getattr(toolset._connection_params, 'server_params', None)
                if server_params and hasattr(server_params, 'args'):
                    args_str = ' '.join(server_params.args)
                    if '@amap/amap-maps-mcp-server' in args_str:
                        return 'Amap Maps Server'
                    elif 'mcp-server-time' in args_str:
                        return 'Time Server'
                    elif 'mcp-server-fetch' in args_str:
                        return 'Fetch Server'
                    elif 'server-memory' in args_str:
                        return 'Memory Server'
            return 'Unknown Server'
        except Exception:
            return 'Unknown Server'
    
    def get_status_report(self) -> Dict[str, Any]:
        """获取工具注册状态报告"""
        return {
            'total_tools': len(self.tools_by_name),
            'tools_by_server': {
                server: len(tools) for server, tools in self.tools_by_server.items()
            },
            'available_tools': list(self.tools_by_name.keys()),
            'initialization_status': self.initialization_status
        }

class AsyncMCPToolInitializer:
    """异步MCP工具初始化器"""
    
    def __init__(self):
        self.initialized_toolsets = []
        self.failed_configs = []
        self.connection_details = {}
    
    async def initialize_all_tools_async(self) -> Tuple[List[MCPToolset], Dict[str, Any]]:
        """异步初始化所有MCP工具"""
        logger.info("🚀 Starting async MCP tool initialization...")
        
        # 获取所有配置
        configs = MCPToolConfig.get_base_configs()
        amap_config = MCPToolConfig.get_amap_config()
        if amap_config:
            configs.append(amap_config)
        
        logger.info(f"📋 Found {len(configs)} MCP server configurations")
        
        # 并行初始化工具（限制并发数以避免资源竞争）
        semaphore = asyncio.Semaphore(3)  # 最多同时初始化3个工具
        tasks = [
            self._initialize_single_tool_with_semaphore(semaphore, config) 
            for config in configs
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果
        for config, result in zip(configs, results):
            if isinstance(result, Exception):
                error_msg = str(result)
                logger.error(f"❌ {config.name} initialization failed: {error_msg}")
                self.failed_configs.append({
                    'name': config.name,
                    'error': error_msg,
                    'required': config.required
                })
                self.connection_details[config.name] = {
                    'status': 'failed',
                    'error': error_msg,
                    'required': config.required
                }
            elif result:
                logger.info(f"✅ {config.name} initialized successfully")
                self.initialized_toolsets.append(result)
                self.connection_details[config.name] = {
                    'status': 'success',
                    'required': config.required
                }
        
        # 创建状态报告
        status_report = self._create_initialization_report()
        
        logger.info(f"🎯 Initialization complete: {len(self.initialized_toolsets)} successful, {len(self.failed_configs)} failed")
        
        return self.initialized_toolsets, status_report
    
    async def _initialize_single_tool_with_semaphore(self, semaphore: asyncio.Semaphore, config: MCPServerConfig) -> Optional[MCPToolset]:
        """使用信号量限制并发的工具初始化"""
        async with semaphore:
            return await self._initialize_single_tool_async(config)
    
    async def _initialize_single_tool_async(self, config: MCPServerConfig) -> Optional[MCPToolset]:
        """异步初始化单个工具"""
        try:
            logger.info(f"🔄 Initializing {config.name}...")
            
            # 预检查
            if not self._pre_check_config(config):
                return None
            
            # 创建连接参数
            server_params = StdioServerParameters(
                command=config.command,
                args=config.args,
                env=config.env_vars
            )
            
            connection_params = StdioConnectionParams(
                server_params=server_params,
                timeout=float(config.timeout)
            )
            
            # 创建工具集
            toolset = MCPToolset(
                connection_params=connection_params,
                tool_filter=config.tool_filter
            )
            
            # 验证工具集可用性
            try:
                tools = await toolset.get_tools()
                logger.info(f"🧪 {config.name} validation: found {len(tools)} tools")
                
                if len(tools) == 0:
                    logger.warning(f"⚠️  {config.name} returned no tools")
                    if config.required:
                        raise Exception(f"Required server {config.name} has no available tools")
                
                return toolset
                
            except Exception as validation_error:
                logger.error(f"❌ {config.name} validation failed: {str(validation_error)}")
                if config.required:
                    raise validation_error
                return None
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize {config.name}: {str(e)}")
            if config.required:
                raise e
            return None
    
    def _pre_check_config(self, config: MCPServerConfig) -> bool:
        """预检查配置"""
        import subprocess
        import shutil
        
        # 检查命令可用性
        if not shutil.which(config.command):
            logger.warning(f"⚠️  Command '{config.command}' not found for {config.name}")
            return False
        
        # 验证环境变量
        for key, value in config.env_vars.items():
            if not value or len(str(value)) < 8:
                logger.warning(f"⚠️  Invalid environment variable {key} for {config.name}")
                return False
        
        return True
    
    def _create_initialization_report(self) -> Dict[str, Any]:
        """创建初始化报告"""
        successful_tools = [name for name, details in self.connection_details.items() 
                          if details['status'] == 'success']
        failed_tools = [name for name, details in self.connection_details.items() 
                       if details['status'] == 'failed']
        
        return {
            'successful_tools': successful_tools,
            'failed_tools': failed_tools,
            'connection_details': self.connection_details,
            'total_attempted': len(self.connection_details),
            'success_rate': len(successful_tools) / max(1, len(self.connection_details)),
            'critical_failures': [
                name for name, details in self.connection_details.items()
                if details['status'] == 'failed' and details.get('required', False)
            ]
        }

class TravelAgentBuilder:
    """旅行代理构建器"""
    
    def __init__(self):
        self.tool_registry = MCPToolRegistry()
        self.initialization_status = {}
    
    async def build_agent_async(self) -> Tuple[LlmAgent, Dict[str, Any]]:
        """异步构建旅行代理"""
        try:
            logger.info("🏗️  Building travel agent with async MCP integration...")
            
            # 1. 异步初始化MCP工具
            initializer = AsyncMCPToolInitializer()
            toolsets, init_status = await initializer.initialize_all_tools_async()
            
            # 2. 注册工具到注册表
            await self.tool_registry.register_toolsets_async(toolsets)
            
            # 3. 创建增强的旅行规划工具
            travel_tool = self._create_enhanced_travel_planning_tool()
            
            # 4. 构建代理指令
            instruction = self._build_agent_instruction(init_status)
            
            # 5. 创建代理
            agent = LlmAgent(
                name="travel_planning_agent",
                model= "gemini-2.0-flash",
                instruction=instruction,
                tools=toolsets + [travel_tool]
            )
            
            # 6. 合并状态报告
            registry_status = self.tool_registry.get_status_report()
            combined_status = {
                **init_status,
                'registry_status': registry_status,
                'agent_created': True
            }
            
            logger.info("✅ Travel agent built successfully with async MCP integration")
            return agent, combined_status
            
        except Exception as e:
            logger.error(f"❌ Failed to build agent: {str(e)}")
            # 创建后备代理
            fallback_agent = self._create_fallback_agent()
            return fallback_agent, {
                'error': str(e),
                'fallback_mode': True,
                'agent_created': True
            }
    
    def _create_enhanced_travel_planning_tool(self):
        """创建增强的旅行规划工具"""
        def travel_planning_tool_with_async_mcp(
            destination: str,
            departure_location: str,
            start_date: str,
            duration: int,
            budget: float
        ) -> Dict[str, Any]:
            """带有异步MCP集成的旅行规划工具"""
            try:
                logger.info(f"🧳 Planning travel: {departure_location} -> {destination}")
                
                # 创建异步MCP调用器
                def mcp_caller(tool_name: str, arguments: dict, server_name: str = None, **kwargs) -> Dict[str, Any]:
                    """同步包装器用于异步MCP调用，支持server_name参数，解决事件循环冲突"""
                    try:
                        logger.info(f"🔧 MCP caller invoked: tool={tool_name}, server={server_name}, args={arguments}")
                        
                        # 检查是否在异步上下文中
                        try:
                            # 尝试获取当前运行的事件循环
                            current_loop = asyncio.get_running_loop()
                            logger.info("📡 Detected running event loop, using thread executor to avoid conflict")
                            
                            # 在线程池中运行异步操作以避免循环冲突
                            import concurrent.futures
                            import threading
                            
                            def run_in_new_loop():
                                """在新线程中创建新的事件循环"""
                                new_loop = asyncio.new_event_loop()
                                asyncio.set_event_loop(new_loop)
                                try:
                                    logger.info(f"🔄 Running {tool_name} in new thread event loop")
                                    return new_loop.run_until_complete(
                                        self.tool_registry.call_tool_async(tool_name, arguments)
                                    )
                                finally:
                                    new_loop.close()
                                    # 清理线程本地的事件循环设置
                                    asyncio.set_event_loop(None)
                            
                            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                                future = executor.submit(run_in_new_loop)
                                result = future.result(timeout=30)  # 30秒超时
                                
                        except RuntimeError as re:
                            # 没有运行的事件循环，可以直接创建
                            logger.info("🔄 No running event loop detected, creating new one directly")
                            result = asyncio.run(
                                self.tool_registry.call_tool_async(tool_name, arguments)
                            )
                        
                        # 验证结果并添加服务器信息
                        if result and isinstance(result, dict):
                            if result.get('success') and server_name:
                                result['server_name'] = server_name
                            logger.info(f"✅ MCP tool {tool_name} executed successfully: {result.get('success', False)}")
                        else:
                            logger.warning(f"⚠️ MCP tool {tool_name} returned unexpected result format: {type(result)}")
                            
                        return result
                        
                    except concurrent.futures.TimeoutError:
                        error_msg = f"MCP tool {tool_name} timed out after 30 seconds"
                        logger.error(f"⏰ {error_msg}")
                        return {
                            'success': False,
                            'error': error_msg,
                            'tool_name': tool_name,
                            'server_name': server_name
                        }
                    except Exception as e:
                        logger.error(f"❌ MCP caller error for {tool_name}: {str(e)}")
                        logger.error(f"🔍 Exception type: {type(e).__name__}")
                        import traceback
                        logger.debug(f"📋 Full traceback: {traceback.format_exc()}")
                        return {
                            'success': False,
                            'error': f'MCP call failed: {str(e)}',
                            'tool_name': tool_name,
                            'server_name': server_name,
                            'exception_type': type(e).__name__
                        }
                
                # 导入必要的模块
                try:
                    from main import TravelAgent
                    from utils.date_parser import parse_date, get_current_date_info
                except ImportError:
                    try:
                        from travel_agent.main import TravelAgent
                        from travel_agent.utils.date_parser import parse_date, get_current_date_info
                    except ImportError:
                        # Create fallback implementations
                        logger.error("Failed to import TravelAgent - using fallback")
                        class TravelAgent:
                            def __init__(self, use_mcp_tool=None):
                                self.use_mcp_tool = use_mcp_tool
                            def plan_travel(self, **kwargs):
                                return {
                                    'success': False,
                                    'error': 'TravelAgent import failed - module not available',
                                    'fallback': True
                                }
                        
                        def parse_date(date_str):
                            return date_str
                        
                        def get_current_date_info():
                            from datetime import datetime
                            return {'current_date': datetime.now().strftime('%Y-%m-%d')}
                
                # 创建旅行代理
                agent = TravelAgent(use_mcp_tool=mcp_caller)
                
                # 解析日期并规划旅行
                current_info = get_current_date_info()
                parsed_start_date = parse_date(start_date)
                
                logger.info(f"📅 Date parsing: '{start_date}' -> '{parsed_start_date}'")
                
                result = agent.plan_travel(
                    destination=destination,
                    departure_location=departure_location,
                    start_date=parsed_start_date,
                    duration=duration,
                    budget=budget
                )
                
                # 添加MCP集成信息
                if result.get('success'):
                    result['mcp_integration'] = {
                        'available_tools': list(self.tool_registry.tools_by_name.keys()),
                        'servers': list(self.tool_registry.tools_by_server.keys()),
                        'date_parsing': {
                            'original_date': start_date,
                            'parsed_date': parsed_start_date,
                            'current_date': current_info['current_date']
                        }
                    }
                
                return result
                
            except Exception as e:
                logger.error(f"❌ Error in enhanced travel planning: {str(e)}")
                return {
                    'success': False,
                    'error': 'Enhanced travel planning error',
                    'details': str(e)
                }
        
        return travel_planning_tool_with_async_mcp
    
    def _build_agent_instruction(self, init_status: Dict[str, Any]) -> str:
        """构建代理指令"""
        instruction_parts = [
            "You are an expert travel planning assistant with advanced MCP tool integration:",
            "",
            "🎯 CORE CAPABILITIES:",
            "1. INTELLIGENT DATE PARSING: Automatically calculate dates from relative expressions like '后天', '明天', '3天后'",
            "2. COMPREHENSIVE PLANNING: Generate detailed travel plans with attractions, accommodations, dining, transportation",
            "3. VISUAL REPORTS: Create beautiful HTML reports with images and detailed information",
            "4. MULTIPLE OPTIONS: Always provide economic and comfort travel plan options",
            "5. REAL-TIME DATA: Use MCP tools for current weather, maps, and location data",
            ""
        ]
        
        # 添加可用工具的说明
        successful_tools = init_status.get('successful_tools', [])
        if successful_tools:
            instruction_parts.extend([
                "🔧 AVAILABLE MCP TOOLS:",
                f"Successfully initialized: {', '.join(successful_tools)}",
                ""
            ])
            
            if 'Time Server' in successful_tools:
                instruction_parts.append("• TIME: Use time tools for accurate date calculations")
            if 'Amap Maps Server' in successful_tools:
                instruction_parts.append("• MAPS: Use Amap tools for location search, weather, and directions")
            if 'Fetch Server' in successful_tools:
                instruction_parts.append("• WEB: Use fetch tools for real-time web data")
            if 'Memory Server' in successful_tools:
                instruction_parts.append("• MEMORY: Use memory tools for user preferences and history")
        
        # 添加错误处理说明
        failed_tools = init_status.get('failed_tools', [])
        if failed_tools:
            instruction_parts.extend([
                "",
                f"⚠️  UNAVAILABLE TOOLS: {', '.join(failed_tools)}",
                "Use AI-generated content as fallback for unavailable tools."
            ])
        
        instruction_parts.extend([
            "",
            "🎨 OUTPUT REQUIREMENTS:",
            "- Always provide multiple plan options (budget and premium)",
            "- Include detailed daily itineraries",
            "- Add practical travel tips and local insights",
            "- Generate comprehensive HTML reports",
            "- Use current date/time for all calculations"
        ])
        
        return "\n".join(instruction_parts)
    
    def _create_fallback_agent(self) -> LlmAgent:
        """创建后备代理"""
        logger.info("🔄 Creating fallback agent without MCP tools...")
        return LlmAgent(
            name="travel_planning_agent_fallback",
            model= "gemini-2.0-flash",
            instruction=(
                "You are an expert travel planning assistant. Generate detailed travel plans "
                "that include attractions, accommodations, dining, transportation, and budget "
                "optimization. Always provide multiple travel plan options (economic and comfort) "
                "and create beautiful HTML reports with images and detailed information. "
                "Note: MCP tools are currently unavailable, using AI-generated content."
            ),
            tools=[create_travel_planning_tool],
        )

# 异步创建函数
async def create_travel_agent_async() -> Tuple[LlmAgent, Dict[str, Any]]:
    """异步创建旅行代理"""
    builder = TravelAgentBuilder()
    return await builder.build_agent_async()

# 同步包装器（向后兼容）
def create_robust_travel_agent() -> Tuple[LlmAgent, Dict[str, Any]]:
    """创建旅行代理（同步版本，向后兼容）"""
    try:
        logger.info("🚀 Starting travel agent creation...")
        
        # 检查是否已有运行的事件循环
        try:
            loop = asyncio.get_running_loop()
            logger.info("📡 Using existing event loop")
            # 如果已有循环，创建新任务
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, create_travel_agent_async())
                return future.result(timeout=120)  # 2分钟超时
        except RuntimeError:
            # 没有运行的循环，直接运行
            logger.info("🔄 Creating new event loop")
            return asyncio.run(create_travel_agent_async())
            
    except Exception as e:
        logger.error(f"❌ Failed to create travel agent: {str(e)}")
        # 创建最小后备代理
        logger.info("🆘 Creating minimal fallback agent...")
        builder = TravelAgentBuilder()
        return builder._create_fallback_agent(), {
            'error': str(e),
            'fallback_mode': True,
            'minimal_agent': True
        }

# 创建代理实例
try:
    logger.info("🎬 Initializing travel agent...")
    root_agent, mcp_status = create_robust_travel_agent()
    
    # 记录初始化结果
    if mcp_status.get('fallback_mode'):
        logger.warning("⚠️  Travel agent created in fallback mode")
        if mcp_status.get('error'):
            logger.error(f"Error details: {mcp_status['error']}")
    else:
        logger.info("✅ Travel agent created successfully with MCP integration")
        
        # 记录可用工具
        successful_tools = mcp_status.get('successful_tools', [])
        if successful_tools:
            logger.info(f"🔧 Available MCP tools: {', '.join(successful_tools)}")
        
        failed_tools = mcp_status.get('failed_tools', [])
        if failed_tools:
            logger.warning(f"⚠️  Failed MCP tools: {', '.join(failed_tools)}")
    
    logger.info(f"📊 Final status: {mcp_status}")
    
except Exception as e:
    logger.error(f"💥 Critical error during agent initialization: {str(e)}")
    # 最后的后备方案
    root_agent = LlmAgent(
        name="travel_planning_agent_emergency",
        model= "gemini-2.0-flash",
        instruction="You are a travel planning assistant. Generate travel plans using AI knowledge.",
        tools=[create_travel_planning_tool],
    )
    mcp_status = {
        'critical_error': str(e),
        'emergency_mode': True
    }
    logger.info("🆘 Emergency fallback agent created")
