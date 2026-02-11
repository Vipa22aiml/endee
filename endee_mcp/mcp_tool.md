{
  "mcp": {
    "embedddingmodel": {
      "type": "local",
      "command": [
        "npx",
        "-y",
        "@testsprite/testsprite-mcp@latest"
      ],
      "environment": {
        "API_KEY": "sk-user-JwNSm***************"
      }
  },

    "endee-local--embedding model": {
      "type": "remote",
      "url": "http://localhost:54321/mcp",
      "enabled": true
    }
  },
  "$schema": "https://opencode.ai/config.json"
}