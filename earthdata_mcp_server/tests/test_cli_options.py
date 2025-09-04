#!/usr/bin/env python3
"""
Test script to verify that earthdata-mcp-server has all CLI options 
from jupyter-mcp-server available.
"""

import subprocess
import sys
import logging

# Set up basic logging
logging.basicConfig(level=logging.INFO)


def test_cli_options_completeness():
    """Test that all jupyter CLI options are available in earthdata server."""
    print("Testing CLI option completeness...")
    
    try:
        # Test that all jupyter options are available in earthdata server
        result = subprocess.run([
            sys.executable, '-m', 'earthdata_mcp_server.server', 'start', '--help'
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Failed to run earthdata server help command: {result.stderr}")
            return False
        
        expected_options = [
            '--transport', '--provider', '--runtime-url', '--start-new-runtime',
            '--runtime-id', '--runtime-token', '--document-url', '--document-id', 
            '--document-token', '--port'
        ]
        
        missing_options = []
        for option in expected_options:
            if option not in result.stdout:
                missing_options.append(option)
        
        if missing_options:
            print(f"❌ Missing CLI options: {missing_options}")
            print("Available help output:")
            print(result.stdout)
            return False
        else:
            print(f"✅ All expected CLI options are available!")
            print(f"Found {len(expected_options)} options in earthdata-mcp-server")
            return True
            
    except Exception as e:
        print(f"❌ Error during CLI options test: {e}")
        return False


def test_command_availability():
    """Test that all expected commands are available."""
    print("\nTesting command availability...")
    
    try:
        # Test main command help
        result = subprocess.run([
            sys.executable, '-m', 'earthdata_mcp_server.server', '--help'
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Failed to run earthdata server main help: {result.stderr}")
            return False
        
        expected_commands = ['connect', 'start', 'stop']
        
        missing_commands = []
        for command in expected_commands:
            if command not in result.stdout:
                missing_commands.append(command)
        
        if missing_commands:
            print(f"❌ Missing commands: {missing_commands}")
            return False
        else:
            print(f"✅ All expected commands are available!")
            print(f"Found commands: {expected_commands}")
            return True
            
    except Exception as e:
        print(f"❌ Error during command availability test: {e}")
        return False


def test_connect_command_options():
    """Test that connect command has the expected options."""
    print("\nTesting connect command options...")
    
    try:
        result = subprocess.run([
            sys.executable, '-m', 'earthdata_mcp_server.server', 'connect', '--help'
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Failed to run connect command help: {result.stderr}")
            return False
        
        expected_options = [
            '--provider', '--runtime-url', '--runtime-id', '--runtime-token',
            '--document-url', '--document-id', '--document-token', 
            '--earthdata-mcp-server-url'
        ]
        
        missing_options = []
        for option in expected_options:
            if option not in result.stdout:
                missing_options.append(option)
        
        if missing_options:
            print(f"❌ Missing connect command options: {missing_options}")
            return False
        else:
            print(f"✅ All connect command options are available!")
            print(f"Found {len(expected_options)} options for connect command")
            return True
            
    except Exception as e:
        print(f"❌ Error during connect command test: {e}")
        return False


def test_environment_variable_support():
    """Test that environment variables are supported (check source code defines them)."""
    print("\nTesting environment variable support...")
    
    try:
        # Import the server module to check that env vars are defined
        from earthdata_mcp_server import server as earthdata_server
        
        expected_env_vars = [
            'TRANSPORT', 'PROVIDER', 'RUNTIME_URL', 'RUNTIME_TOKEN',
            'DOCUMENT_URL', 'DOCUMENT_ID', 'DOCUMENT_TOKEN'
        ]
        
        # Check that global variables exist (indicating env var support)
        missing_globals = []
        for env_var in expected_env_vars:
            if not hasattr(earthdata_server, env_var):
                missing_globals.append(env_var)
        
        if missing_globals:
            print(f"❌ Missing global variables for env vars: {missing_globals}")
            return False
        else:
            print(f"✅ Environment variable support confirmed!")
            print(f"Found {len(expected_env_vars)} global variables for environment configuration")
            
            # Also check that at least some help text mentions envvar usage
            result = subprocess.run([
                sys.executable, '-m', 'earthdata_mcp_server.server', 'start', '--help'
            ], capture_output=True, text=True)
            
            if 'envvar' in result.stdout.lower():
                print("✅ Help text mentions environment variable support")
            else:
                print("ℹ️  Environment variables supported but not explicitly mentioned in help")
            
            return True
            
    except Exception as e:
        print(f"❌ Error during environment variable test: {e}")
        return False


def main():
    """Run all CLI tests."""
    print("=" * 60)
    print("EARTHDATA-MCP-SERVER CLI OPTIONS TEST")
    print("=" * 60)
    
    tests = [
        test_cli_options_completeness,
        test_command_availability,
        test_connect_command_options,
        test_environment_variable_support
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("CLI TEST SUMMARY")
    print("=" * 60)
    
    if all(results):
        print("🎉 All CLI tests passed! Earthdata-MCP-Server CLI integration is working correctly.")
        return 0
    else:
        print("❌ Some CLI tests failed. Check the output above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
