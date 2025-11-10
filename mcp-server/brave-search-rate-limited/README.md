# Brave Search MCP Server with Rate Limiting

An MCP server for Brave Search with built-in rate limiting (max. 1 call per second).

## Features

- **Rate Limiting**: Automatically max. 1 API call per x seconds
- **Thread-Safe**: Queue-based system prevents race conditions
- **Better Error Handling**: Special handling for rate limit errors (429)
- **Logging**: Clear status messages and emoji icons
- **Local**: Your API keys stay on your machine

## Installation

### Step 1: Create Directory

```bash
mkdir -p ~/mcp-servers/brave-search-rate-limited
cd ~/mcp-servers/brave-search-rate-limited
```

### Step 2: Copy Files

Copy these files to the directory:
- `brave-search-rate-limited.js`
- `package.json`

### Step 3: Install Dependencies

```bash
npm install
```

### Step 4: Make Script Executable

```bash
chmod +x brave-search-rate-limited.js
```

### Step 5: Test (optional but recommended!)

```bash
export BRAVE_API_KEY="your_api_key_here"
./test.sh
```

If everything works, you should see:
```
All tests passed!
```

## Configuration

### Setting up Claude Code

Edit your `~/.claude.json` (or `.mcp.json` in the project directory):

```json
{
  "mcpServers": {
    "brave-search": {
      "command": "node",
      "args": ["/home/YOUR_USERNAME/mcp-servers/brave-search-rate-limited/brave-search-rate-limited.js"],
      "env": {
        "BRAVE_API_KEY": "YOUR_BRAVE_API_KEY"
      }
    }
  }
}
```

**Important:**
- Replace `/home/YOUR_USERNAME/` with your actual path
- Replace `YOUR_BRAVE_API_KEY` with your real API key
- Find the absolute path with: `pwd`

### Restart Claude Code

```bash
# Close Claude Code (if running)
# Then restart:
claude
```

### Check if it works

In Claude Code:
```
/mcp
```

You should see:
```
brave-search: connected
```

## Adjusting Rate Limiting

In the file `brave-search-rate-limited.js`, line 11:

```javascript
const RATE_LIMIT_MS = 1500; // Minimum interval between API calls in milliseconds
```

Changes:
- `1000` = 1 second (standard, recommended)
- `2000` = 2 seconds (very conservative)
- `1500` = 1.5 seconds
- `500` = 0.5 seconds (only if your plan allows it!)

**Warning:** Never set the value below your API limit!

## Usage

Claude Code will automatically use the server when performing web searches.

### What happens internally:

1. Claude Code wants to perform 2 searches quickly in succession
2. The Rate Limiter accepts both requests
3. First search is executed immediately
4. Second search automatically waits x seconds
5. You get both results without exceeding your API limit!

### Log Output

The server shows you what's happening:

```
[Brave Search] Searching for: "Python Tutorials"
[Brave Search] Success - 10 results found

[Rate Limiter] Waiting 743ms... (1 more in queue)
[Brave Search] Searching for: "JavaScript Tutorials"
[Brave Search] Success - 10 results found
```

## How It Works

### The Problem

Brave API has a rate limit (e.g., 1 call per second on the free plan). If you make requests too fast:

```
Request 1 -> OK
Request 2 (0.1s later) -> 429 Error (Rate Limit!)
```

### The Solution

This server uses a **queue system**:

1. All requests go into a queue
2. The first request is processed immediately
3. Each subsequent request waits automatically
4. No API limit violations!

```
Request 1 -> [Immediate] -> OK
Request 2 -> [Wait 1s] -> OK
Request 3 -> [Wait 1s] -> OK
```

### Technical Details

The `RateLimiter` class:
- Maintains a queue of pending requests
- Calculates wait time until next allowed call
- Processes requests sequentially
- Thread-safe through async/await
