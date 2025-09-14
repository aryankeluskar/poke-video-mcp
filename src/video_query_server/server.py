"""Video Query MCP Server
Provides video search capabilities using the photographic video processing API
"""

from mcp.server.fastmcp import Context, FastMCP
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import httpx
import asyncio
from datetime import datetime

from smithery.decorators import smithery


class ConfigSchema(BaseModel):
    user_id: str = Field(..., description="Your Flashback account user ID - this identifies your video collection")


# For servers with configuration:
@smithery.server(config_schema=ConfigSchema)
# For servers without configuration, simply use:
# @smithery.server()
def create_server():
    """Create and configure the MCP server."""

    # Create your FastMCP server
    server = FastMCP("Video Query")

    # Add video query tool
    @server.tool()
    async def query_videos(query: str, ctx: Context, max_results: int = 10) -> str:
        """Search for video clips based on natural language query. Returns detailed AI-generated descriptions and URLs of relevant video segments."""
        try:
            session_config = ctx.session_config

            if not session_config.user_id:
                return "Error: User ID is required in configuration"

            # Call the new video processing API endpoint that returns descriptions
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://jzflint--video-processing-api-fastapi-app.modal.run/retrieve-clips-with-descriptions",
                    json={
                        "user_id": session_config.user_id,
                        "query": query,
                        "top_k": min(max_results, 15)  # Limit to 15 as requested
                    }
                )

                if response.status_code != 200:
                    return f"Error querying videos: {response.status_code} - {response.text}"

                data = response.json()
                clips = data.get("clips", [])

                if not clips:
                    return f"No video clips found for query: '{query}'\n\nThis could mean:\n• No videos have been uploaded for this user\n• The query doesn't match any video content\n• Try using different search terms or keywords"

                # Format results with AI-generated descriptions and URLs
                results = []
                for i, clip in enumerate(clips[:15], 1):  # Limit to top 15
                    chunk_id = clip['chunk_id']
                    description = clip['description']

                    # Format expiry time nicely
                    expires_str = clip['expires_at'][:19] if 'T' in clip['expires_at'] else clip['expires_at']

                    results.append(
                        f"{i}. **Relevance Score: {clip['score']:.3f}**\n"
                        f"   📄 **AI Description:** {description}\n"
                        f"   📹 **Video URL:** {clip['url']}\n"
                        f"   ⏰ **URL Expires:** {expires_str}\n"
                        f"   🎬 **Video ID:** {clip['video_id'][:8]}...\n"
                        f"   📝 **Chunk ID:** {chunk_id[:8]}..."
                    )

                summary = (
                    f"🎯 **Found {len(clips)} relevant video clips for query:** '{query}'\n\n"
                    f"📊 **Results sorted by relevance score (higher = more relevant)**\n\n"
                )

                return summary + "\n\n".join(results) + "\n\n" + (
                    "💡 **Usage Tips:**\n"
                    "• Read the AI-generated descriptions to understand video content before clicking\n"
                    "• Click video URLs to view the actual clips\n"
                    "• URLs expire after the specified time - use them promptly\n"
                    "• Each video segment represents approximately 30 seconds of content\n"
                    "• Descriptions include both visual content analysis and audio transcription"
                )

        except Exception as e:
            return f"Error searching videos: {str(e)}\n\nPlease ensure:\n• Your user_id is configured correctly\n• The video processing API is accessible\n• You have internet connectivity"

    @server.tool()
    async def get_setup_instructions() -> str:
        """Get instructions for setting up the video query system"""
        return """# Video Query MCP Setup Instructions

## What you need:
1. **Your Flashback User ID** - This identifies your personal video collection

## How to configure:
When Poke prompts you to configure this MCP server, provide:
- **user_id**: Your unique Flashback account identifier

## How it works:
1. Videos are uploaded and processed through the Flashback video processing system
2. Each video is split into ~30-second segments
3. AI generates descriptions of visual content and transcribes audio
4. Everything is stored in a searchable vector database
5. You can search using natural language (e.g., "person talking", "red car", "meeting room")

## Usage:
- Use `query_videos` to search for video content
- Specify how many results you want (max 15)
- Get back video URLs that you can click to watch
- URLs expire after 1 hour for security

## Example searches:
- "person giving presentation"
- "dog running in park"
- "discussion about project deadlines"
- "someone cooking in kitchen"

No authentication needed - just your user ID to access your video collection!"""

    # Add a resource for API information
    @server.resource("api://video-processing")
    def video_api_info() -> str:
        """Information about the video processing API endpoints and capabilities."""
        return (
            "Video Processing API Information:\n"
            "Base URL: https://jzflint--video-processing-api-fastapi-app.modal.run/\n\n"
            "Endpoints:\n"
            "- POST /process-video: Upload and process video files\n"
            "- POST /process-photo: Upload and process photo files\n"
            "- POST /retrieve-clips: Search for video clips using natural language\n"
            "- GET /health: Check API status\n\n"
            "The API processes videos by:\n"
            "1. Splitting videos into chunks\n"
            "2. Generating transcriptions using OpenAI Whisper\n"
            "3. Creating visual descriptions using Anthropic Claude\n"
            "4. Storing in vector database (Pinecone) for semantic search\n"
            "5. Providing presigned URLs for video access"
        )

    # Add a prompt for video search
    @server.prompt()
    def search_videos_prompt(topic: str) -> list:
        """Generate a prompt to search for videos about a specific topic."""
        return [
            {
                "role": "user",
                "content": f"Search for video clips related to: {topic}. Please use the query_videos tool to find relevant content.",
            },
        ]

    return server
