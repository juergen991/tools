#!/usr/bin/env node

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";

// Configuration
const RATE_LIMIT_MS = 1500; // Minimum interval between API calls in milliseconds
const RATE_LIMIT_SECONDS = (RATE_LIMIT_MS / 1000).toFixed(1); // For display in seconds with one decimal place

// Rate Limiter with real queue for parallel requests
class RateLimiter {
  constructor(minDelayMs = 1000) {
    this.minDelay = minDelayMs;
    this.lastCallTime = 0;
    this.pending = [];
    this.processing = false;
  }

  async throttle() {
    return new Promise((resolve) => {
      // Add this request to the queue
      this.pending.push(resolve);
      
      // Start processing if not already active
      this.processQueue();
    });
  }

  async processQueue() {
    // Prevent parallel processing
    if (this.processing) {
      return;
    }
    
    this.processing = true;
    
    while (this.pending.length > 0) {
      const resolve = this.pending.shift();
      
      // Calculate how long we need to wait
      const now = Date.now();
      const timeSinceLastCall = now - this.lastCallTime;
      
      if (timeSinceLastCall < this.minDelay) {
        const waitTime = this.minDelay - timeSinceLastCall;
        console.error(`[Rate Limiter] Waiting ${waitTime}ms... (${this.pending.length} more in queue)`);
        await new Promise(r => setTimeout(r, waitTime));
      }
      
      // Update timestamp
      this.lastCallTime = Date.now();
      
      // Release this request
      resolve();
    }
    
    this.processing = false;
  }
}

// Server Setup
const server = new Server(
  {
    name: "brave-search-rate-limited",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Initialize Rate Limiter
const rateLimiter = new RateLimiter(RATE_LIMIT_MS);

// API Key from environment variable
const BRAVE_API_KEY = process.env.BRAVE_API_KEY;

if (!BRAVE_API_KEY) {
  console.error("Error: BRAVE_API_KEY environment variable not set");
  process.exit(1);
}

// Define tools
server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "brave_search",
      description: "Search the web using Brave Search API",
      inputSchema: {
        type: "object",
        properties: {
          query: {
            type: "string",
            description: "The search query"
          },
          count: {
            type: "number",
            description: "Number of results (default: 10)",
            default: 10
          }
        },
        required: ["query"]
      }
    }
  ]
}));

// Tool Handler with Rate Limiting
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  if (request.params.name === "brave_search") {
    const { query, count = 10 } = request.params.arguments;
    
    try {
      // IMPORTANT: Rate Limiting BEFORE API call
      await rateLimiter.throttle();
      
      console.error(`[Brave Search] Searching for: "${query}"`);
      
      const url = new URL("https://api.search.brave.com/res/v1/web/search");
      url.searchParams.set("q", query);
      url.searchParams.set("count", count.toString());
      
      const response = await fetch(url.toString(), {
        headers: {
          "Accept": "application/json",
          "Accept-Encoding": "gzip",
          "X-Subscription-Token": BRAVE_API_KEY
        }
      });
      
      if (!response.ok) {
        // Special handling for Rate Limit errors
        if (response.status === 429) {
          console.error(`[Brave Search] Rate Limit reached! Status: ${response.status}`);
          return {
            content: [
              {
                type: "text",
                text: `Rate Limit reached! The Brave API currently does not allow any more requests. Please wait a moment and try again.`
              }
            ],
            isError: true
          };
        }
        
        // Other HTTP errors
        const errorText = await response.text().catch(() => response.statusText);
        console.error(`[Brave Search] API Error ${response.status}: ${errorText}`);
        throw new Error(`Brave API Error: ${response.status} - ${errorText}`);
      }
      
      const data = await response.json();
      
      // Check if response is valid
      if (!data) {
        throw new Error("No data received from Brave API");
      }
      
      console.error(`[Brave Search] Success - ${data.web?.results?.length || 0} results found`);
      
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(data, null, 2)
          }
        ]
      };
    } catch (error) {
      console.error(`[Brave Search] Error:`, error.message);
      return {
        content: [
          {
            type: "text",
            text: `Search error: ${error.message}`
          }
        ],
        isError: true
      };
    }
  }
  
  throw new Error(`Unknown tool: ${request.params.name}`);
});

// Start server
const transport = new StdioServerTransport();
server.connect(transport);

console.error("╔════════════════════════════════════════════════════════╗");
console.error("║  Brave Search MCP Server (Rate-Limited)                ║");
console.error(`║  Rate Limit: 1 call every ${RATE_LIMIT_SECONDS} seconds                  ║`);
console.error("║  Status: Started                                       ║");
console.error("╚════════════════════════════════════════════════════════╝");
