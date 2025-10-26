"""
MCP (Model Context Protocol) Bridge

Discovers and integrates MCP servers for external tool capabilities.
Provides extensibility point for adding new integrations.
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional


class MCPServer:
    """Represents a configured MCP server."""
    
    def __init__(
        self,
        name: str,
        description: str,
        transport: str,
        command: str,
        args: List[str],
        env: Dict[str, str],
        config: Dict[str, Any],
        enabled: bool
    ):
        self.name = name
        self.description = description
        self.transport = transport
        self.command = command
        self.args = args
        self.env = env
        self.config = config
        self.enabled = enabled
    
    def __repr__(self) -> str:
        return f"MCPServer(name='{self.name}', enabled={self.enabled})"


def load_mcp_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load MCP server configuration from JSON file.
    
    Args:
        config_path: Path to mcp_servers.json. Defaults to config/mcp_servers.json.
    
    Returns:
        Parsed configuration dictionary.
    
    Raises:
        FileNotFoundError: If configuration file doesn't exist.
        json.JSONDecodeError: If configuration is invalid JSON.
    """
    if config_path is None:
        config_path = Path(__file__).parent.parent / "config" / "mcp_servers.json"
    else:
        config_path = Path(config_path)
    
    if not config_path.exists():
        raise FileNotFoundError(
            f"MCP configuration not found: {config_path}\n"
            f"Create config/mcp_servers.json with server definitions."
        )
    
    with open(config_path, 'r') as f:
        return json.load(f)


def discover_servers(config_path: Optional[str] = None) -> List[MCPServer]:
    """
    Discover all configured MCP servers.
    
    Args:
        config_path: Path to mcp_servers.json. Defaults to config/mcp_servers.json.
    
    Returns:
        List of MCPServer objects (only enabled servers).
    
    Examples:
        >>> servers = discover_servers()
        >>> print(f"Found {len(servers)} enabled MCP servers")
        >>> for server in servers:
        ...     print(f"  - {server.name}: {server.description}")
    """
    try:
        config = load_mcp_config(config_path)
        servers = []
        
        for server_config in config.get('servers', []):
            # Resolve environment variables in config
            resolved_env = {}
            for key, value in server_config.get('env', {}).items():
                # Replace ${VAR_NAME} with environment variable value
                if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
                    env_var = value[2:-1]
                    resolved_env[key] = os.getenv(env_var, '')
                else:
                    resolved_env[key] = value
            
            server = MCPServer(
                name=server_config.get('name', 'unknown'),
                description=server_config.get('description', ''),
                transport=server_config.get('transport', 'stdio'),
                command=server_config.get('command', ''),
                args=server_config.get('args', []),
                env=resolved_env,
                config=server_config.get('config', {}),
                enabled=server_config.get('enabled', False)
            )
            
            # Only return enabled servers
            if server.enabled:
                servers.append(server)
        
        return servers
    
    except FileNotFoundError as e:
        print(f"Warning: {e}")
        return []
    
    except json.JSONDecodeError as e:
        print(f"Error: Invalid MCP configuration JSON: {e}")
        return []


def get_server_by_name(name: str, config_path: Optional[str] = None) -> Optional[MCPServer]:
    """
    Get specific MCP server by name.
    
    Args:
        name: Name of the server to retrieve.
        config_path: Path to mcp_servers.json.
    
    Returns:
        MCPServer object if found and enabled, None otherwise.
    
    Examples:
        >>> fs_server = get_server_by_name('filesystem')
        >>> if fs_server:
        ...     print(f"Filesystem server found: {fs_server.description}")
    """
    servers = discover_servers(config_path)
    for server in servers:
        if server.name == name:
            return server
    return None


def server_to_langchain_tools(server: MCPServer) -> List:
    """
    Convert MCP server to LangChain tool definitions.
    
    TODO: This is a stub for future implementation. Full MCP integration requires:
    1. Spawning stdio/JSON-RPC client process
    2. Discovering available server operations/methods
    3. Wrapping each operation as a LangChain @tool
    4. Managing server lifecycle (start, stop, restart)
    
    Current implementation returns empty list. Extend this function to:
    - Launch MCP server subprocess with specified command and args
    - Establish JSON-RPC communication channel
    - Query server capabilities (list_methods, describe_method, etc.)
    - Generate LangChain tool wrappers dynamically
    
    Args:
        server: MCPServer configuration to convert.
    
    Returns:
        List of LangChain tool functions (currently empty - TODO).
    
    Extensibility Example:
        def server_to_langchain_tools(server: MCPServer) -> List:
            if server.name == 'filesystem':
                return [
                    create_fs_read_tool(server),
                    create_fs_write_tool(server),
                    create_fs_list_tool(server)
                ]
            elif server.name == 'github':
                return [
                    create_github_issues_tool(server),
                    create_github_pr_tool(server)
                ]
            # ... more server types
            return []
    """
    # Stub implementation
    print(f"TODO: Implement MCP bridge for server '{server.name}'")
    print(f"  Transport: {server.transport}")
    print(f"  Command: {server.command} {' '.join(server.args)}")
    print(f"  Config: {server.config}")
    
    return []


def get_all_mcp_tools(config_path: Optional[str] = None) -> List:
    """
    Get all LangChain tools from all enabled MCP servers.
    
    Args:
        config_path: Path to mcp_servers.json.
    
    Returns:
        List of all tool functions from all enabled MCP servers.
    
    Note: Currently returns empty list until server_to_langchain_tools is implemented.
    
    Examples:
        >>> tools = get_all_mcp_tools()
        >>> print(f"Loaded {len(tools)} MCP tools")
    """
    servers = discover_servers(config_path)
    all_tools = []
    
    for server in servers:
        tools = server_to_langchain_tools(server)
        all_tools.extend(tools)
    
    return all_tools


# Extensibility Guide:
#
# To add full MCP support, implement server_to_langchain_tools() with:
#
# 1. Server Process Management:
#    - Use subprocess.Popen() to start server with stdio transport
#    - Manage process lifecycle (health checks, restart on failure)
#
# 2. JSON-RPC Communication:
#    - Send JSON-RPC requests to server's stdin
#    - Read JSON-RPC responses from server's stdout
#    - Handle errors and timeouts
#
# 3. Dynamic Tool Creation:
#    - Query server for available methods
#    - For each method, create a @tool decorated function
#    - Include proper type hints and docstrings from server metadata
#
# 4. Example Implementation Skeleton:
#
#    from langchain.tools import tool
#    import subprocess
#    import json
#
#    def server_to_langchain_tools(server: MCPServer) -> List:
#        # Start server process
#        process = subprocess.Popen(
#            [server.command] + server.args,
#            stdin=subprocess.PIPE,
#            stdout=subprocess.PIPE,
#            stderr=subprocess.PIPE,
#            text=True,
#            env={**os.environ, **server.env}
#        )
#        
#        # Discover methods via JSON-RPC
#        methods = rpc_call(process, "list_methods", {})
#        
#        # Create tool for each method
#        tools = []
#        for method in methods:
#            @tool
#            def dynamic_tool(params: dict) -> str:
#                return rpc_call(process, method['name'], params)
#            
#            dynamic_tool.__name__ = method['name']
#            dynamic_tool.__doc__ = method.get('description', '')
#            tools.append(dynamic_tool)
#        
#        return tools
#
# 5. Server-Specific Implementations:
#    - filesystem: read_file, write_file, list_dir, search_files
#    - github: create_issue, list_prs, comment_on_pr
#    - jira: create_ticket, update_ticket, search_tickets
#    - browser: navigate, click, screenshot, extract_text
