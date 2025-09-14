# Video Query MCP Server

An MCP (Model Context Protocol) server that provides video search capabilities using natural language queries. This server interfaces with the Flashback video processing API to search through your personal video collection.

## Features

- 🔍 **Natural Language Search**: Query videos using everyday language (e.g., "person giving presentation", "dog running in park")
- 🤖 **AI-Generated Descriptions**: Returns detailed descriptions of video content including visual analysis and audio transcription
- 🎬 **Video Clips**: Get direct URLs to relevant 30-second video segments
- ⚡ **Fast & Secure**: Presigned URLs with 1-hour expiration for secure access
- 📊 **Relevance Scoring**: Results ranked by semantic similarity to your query

## Setup

### Prerequisites
- Your Flashback account user ID
- Access to the Flashback video processing system

### Configuration
When connecting this MCP server to Poke or other MCP clients, you'll need to provide:
- **user_id**: Your unique Flashback account identifier (e.g., `4087fce3-3d86-4047-b35f-4004b4c19192`)

### Development
1. Run the server:
   ```bash
   uv run dev
   ```

2. Test interactively:
   ```bash
   uv run playground
   ```

### Usage Examples

**Query videos:**
```
query_videos("person talking", max_results=5)
```

**Get setup help:**
```
get_setup_instructions()
```

## How It Works

1. **Video Processing**: Videos uploaded to Flashback are automatically:
   - Split into ~30-second segments
   - Analyzed with AI for visual content
   - Transcribed for audio content
   - Stored in a searchable vector database

2. **Search Process**: When you search:
   - Your query is converted to embeddings
   - The system finds matching video segments
   - Returns descriptions and URLs for relevant clips

3. **Results**: Each result includes:
   - AI-generated description of the video content
   - Relevance score (0-1, higher = more relevant)
   - Direct URL to view the video segment
   - Expiration time for the URL

## API Reference

### Tools

#### `query_videos(query: str, max_results: int = 10) -> str`
Search for video clips based on natural language query.

**Parameters:**
- `query`: Natural language description of what you're looking for
- `max_results`: Maximum number of results to return (1-15)

**Returns:** Formatted text with video descriptions and URLs

#### `get_setup_instructions() -> str`
Get detailed setup instructions for the video query system.

**Returns:** Complete setup and usage guide

### Resources

- `api://video-processing`: Information about the underlying video processing API

## Examples

```python
# Search for specific content
query_videos("meeting discussion about deadlines")
query_videos("someone cooking in kitchen")
query_videos("red car driving")

# Limit results
query_videos("presentation", max_results=3)
```

## Troubleshooting

- **No results found**: Check that videos have been uploaded to your Flashback account
- **"No description available"**: Older videos may need to be re-processed for full descriptions
- **Expired URLs**: Video URLs expire after 1 hour for security - request fresh results if needed

## Technical Details

- **Backend**: FastAPI service deployed on Modal
- **Vector Database**: Pinecone for semantic search
- **AI Models**: Anthropic Claude for visual analysis, OpenAI Whisper for transcription
- **Storage**: Google Cloud Storage for video files

## Deploy

Ready to deploy? Push your code to GitHub and deploy to Smithery:

1. Create a new repository at [github.com/new](https://github.com/new)

2. Initialize git and push to GitHub:
   ```bash
   git add .
   git commit -m "Video Query MCP Server 🎬"
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
   git push -u origin main
   ```

3. Deploy your server to Smithery at [smithery.ai/new](https://smithery.ai/new)