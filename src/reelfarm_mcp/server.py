"""
ReelFarm MCP Server

MCP server that wraps the ReelFarm REST API.
Base URL: https://reel.farm/api/v1
Auth: Bearer token (rf_*) via REELFARM_API_KEY env var.
Rate limit: 20 requests per 60-second sliding window.
"""

import os
import json
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Server setup
# ---------------------------------------------------------------------------

mcp = FastMCP(
    "ReelFarm",
    description="Create slideshows, manage automations, publish to TikTok, and more via the ReelFarm API.",
)

BASE_URL = "https://reel.farm/api/v1"


def _get_api_key() -> str:
    """Return the API key from environment or raise."""
    key = os.environ.get("REELFARM_API_KEY")
    if not key:
        raise ValueError(
            "REELFARM_API_KEY environment variable is not set. "
            "Get your key from https://reel.farm/dashboard → Settings → API Keys."
        )
    return key


def _headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {_get_api_key()}",
        "Content-Type": "application/json",
    }


async def _request(
    method: str,
    path: str,
    *,
    params: dict[str, Any] | None = None,
    json_body: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Make an authenticated request to the ReelFarm API."""
    url = f"{BASE_URL}{path}"
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.request(
            method,
            url,
            headers=_headers(),
            params=params,
            json=json_body,
        )
        resp.raise_for_status()
        return resp.json()


# ===========================================================================
# ACCOUNT
# ===========================================================================


@mcp.tool()
async def get_account() -> dict:
    """Get account info including subscription tier, remaining credits, and billing cycle reset date."""
    return await _request("GET", "/account")


# ===========================================================================
# SLIDESHOWS
# ===========================================================================


@mcp.tool()
async def generate_slideshow(
    additional_context: str,
    images: list[str] | None = None,
) -> dict:
    """Generate a slideshow from a natural-language prompt. AI picks text, images, and styling.

    Rendering is async (~45s). Poll slideshow_status to track progress.

    Args:
        additional_context: Prompt controlling topic, slide count, text items, fonts, tone, etc.
        images: Optional list of image URLs for slide backgrounds (0-indexed: images[0] → slide 0).
    """
    body: dict[str, Any] = {"additional_context": additional_context}
    if images:
        body["images"] = images
    return await _request("POST", "/slideshows/generate", json_body=body)


@mcp.tool()
async def create_slideshow(
    slides: list[dict],
    title: str | None = None,
    aspect_ratio: str | None = None,
    text_position: str | None = None,
    export_as_video: bool | None = None,
    duration: int | None = None,
    is_bg_overlay_on: bool | None = None,
    is_bg_overlay_on_hook_image: bool | None = None,
    background_opacity: int | None = None,
    keep_original_aspect_ratio: bool | None = None,
) -> dict:
    """Create a slideshow with full manual control over every slide's image, text, and styling.

    No AI generation — renders in ~10 seconds.

    Args:
        slides: Array of slide objects. Each slide has image_url or image_urls, text_items, etc.
        title: Slideshow title (default "API Slideshow").
        aspect_ratio: "4:5" (default), "9:16", "1:1", or "16:9".
        text_position: "top", "center" (default), or "bottom".
        export_as_video: Export as .mp4 in addition to rendered images.
        duration: Seconds per slide in video (default 4). Only applies when export_as_video is true.
        is_bg_overlay_on: Dark overlay on body slides.
        is_bg_overlay_on_hook_image: Dark overlay on hook slide.
        background_opacity: Overlay opacity 0-100 (default 20).
        keep_original_aspect_ratio: Use each image's native aspect ratio.
    """
    body: dict[str, Any] = {"slides": slides}
    for key in [
        "title", "aspect_ratio", "text_position", "export_as_video",
        "duration", "is_bg_overlay_on", "is_bg_overlay_on_hook_image",
        "background_opacity", "keep_original_aspect_ratio",
    ]:
        val = locals()[key]
        if val is not None:
            body[key] = val
    return await _request("POST", "/slideshows/create", json_body=body)


@mcp.tool()
async def slideshow_status(slideshow_id: int) -> dict:
    """Check slideshow generation/rendering progress. Poll every 5-10 seconds.

    Status flow: draft → generating → rendering → completed (or failed).
    When a video export exists, also returns video_id and video_status.

    Args:
        slideshow_id: The slideshow ID from generate or create.
    """
    return await _request("GET", f"/slideshows/{slideshow_id}/status")


# ===========================================================================
# AUTOMATIONS
# ===========================================================================


@mcp.tool()
async def create_automation(
    tiktok_account_id: str,
    schedule: list[dict],
    title: str | None = None,
    product_id: int | None = None,
    slideshow_hooks: list[str] | None = None,
    style: str | None = None,
    language: str | None = None,
    tiktok_post_settings: dict | None = None,
    image_settings: dict | None = None,
) -> dict:
    """Create a recurring automation that generates and publishes slideshows to TikTok on a cron schedule.

    Args:
        tiktok_account_id: Target TikTok account ID (from list_tiktok_accounts).
        schedule: Array of cron objects, e.g. [{"cron": "0 14 * * *"}]. Pacific time.
        title: Descriptive name for this automation.
        product_id: Link to a product in the products table.
        slideshow_hooks: Hook/topic templates the AI rotates through.
        style: Natural-language prompt controlling text items, fonts, sizes, positions, tone.
        language: Language for generated content (default "English").
        tiktok_post_settings: TikTok posting config (caption, visibility, auto_post, etc.).
        image_settings: Image and display config (aspect_ratio, overlays, collections, etc.).
    """
    body: dict[str, Any] = {
        "tiktok_account_id": tiktok_account_id,
        "schedule": schedule,
    }
    for key in [
        "title", "product_id", "slideshow_hooks", "style", "language",
        "tiktok_post_settings", "image_settings",
    ]:
        val = locals()[key]
        if val is not None:
            body[key] = val
    return await _request("POST", "/automations", json_body=body)


@mcp.tool()
async def list_automations() -> dict:
    """List all automations belonging to the authenticated user."""
    return await _request("GET", "/automations")


@mcp.tool()
async def get_automation(automation_id: str) -> dict:
    """Get full details of a single automation.

    Args:
        automation_id: The automation UUID.
    """
    return await _request("GET", f"/automations/{automation_id}")


@mcp.tool()
async def update_automation(
    automation_id: str,
    action: str | None = None,
    title: str | None = None,
    slideshow_hooks: list[str] | None = None,
    style: str | None = None,
    language: str | None = None,
    tiktok_account_id: str | None = None,
    tiktok_post_settings: dict | None = None,
    product_id: int | None = None,
    image_settings: dict | None = None,
) -> dict:
    """Update automation settings, or pause/unpause it.

    To pause: set action="pause". To unpause: set action="unpause".
    For config updates, set the fields you want to change.

    Args:
        automation_id: The automation UUID.
        action: "pause" or "unpause" (mutually exclusive with other fields).
        title: Update the title.
        slideshow_hooks: Replace the hooks list.
        style: Update the style prompt.
        language: Update the language.
        tiktok_account_id: Change target TikTok account.
        tiktok_post_settings: Update TikTok posting settings.
        product_id: Change linked product.
        image_settings: Update image/collection settings.
    """
    body: dict[str, Any] = {}
    if action:
        body["action"] = action
    else:
        for key in [
            "title", "slideshow_hooks", "style", "language",
            "tiktok_account_id", "tiktok_post_settings", "product_id",
            "image_settings",
        ]:
            val = locals()[key]
            if val is not None:
                body[key] = val
    return await _request("PATCH", f"/automations/{automation_id}", json_body=body)


@mcp.tool()
async def delete_automation(automation_id: str) -> dict:
    """Permanently delete an automation and all its scheduled jobs.

    Args:
        automation_id: The automation UUID.
    """
    return await _request("DELETE", f"/automations/{automation_id}")


@mcp.tool()
async def run_automation(
    automation_id: str,
    hook: str | None = None,
    mode: str | None = None,
) -> dict:
    """Trigger a one-off slideshow generation using the automation's saved settings.

    Does not affect the cron schedule. To find the video, note the time before calling,
    then poll list_videos with automation_id and created_after filters.

    Args:
        automation_id: The automation UUID.
        hook: Override the hook/topic for this single run.
        mode: "export" (default, generates video) or "draft_only" (no video).
    """
    body: dict[str, Any] = {}
    if hook:
        body["hook"] = hook
    if mode:
        body["mode"] = mode
    return await _request("POST", f"/automations/{automation_id}/run", json_body=body)


# ===========================================================================
# AUTOMATION SCHEDULES
# ===========================================================================


@mcp.tool()
async def add_schedule(automation_id: str, cron: str) -> dict:
    """Add a new cron schedule to an automation.

    Args:
        automation_id: The automation UUID.
        cron: Cron expression in Pacific time, e.g. "0 14 * * *" for 2pm daily.
    """
    return await _request(
        "POST",
        f"/automations/{automation_id}/schedule",
        json_body={"cron": cron},
    )


@mcp.tool()
async def update_schedule(
    automation_id: str,
    job_id: str | None = None,
    cron: str | None = None,
    actions: list[dict] | None = None,
) -> dict:
    """Update one or more schedule jobs on an automation.

    For a single update, provide job_id and cron.
    For batch operations, provide actions array with {type, job_id, cron} objects.

    Args:
        automation_id: The automation UUID.
        job_id: The job to update (single update mode).
        cron: New cron expression (single update mode).
        actions: Array of batch operations [{type: "update"|"delete", job_id, cron}].
    """
    if actions:
        body: dict[str, Any] = {"actions": actions}
    else:
        body = {"job_id": job_id, "cron": cron}
    return await _request(
        "PATCH",
        f"/automations/{automation_id}/schedule",
        json_body=body,
    )


@mcp.tool()
async def delete_schedule(automation_id: str, job_id: str) -> dict:
    """Remove a single schedule job from an automation.

    Args:
        automation_id: The automation UUID.
        job_id: The job to remove.
    """
    return await _request(
        "DELETE",
        f"/automations/{automation_id}/schedule",
        json_body={"job_id": job_id},
    )


# ===========================================================================
# VIDEOS
# ===========================================================================


@mcp.tool()
async def list_videos(
    automation_id: str | None = None,
    video_type: str | None = None,
    status: str | None = None,
    finished: str | None = None,
    failed: str | None = None,
    created_after: str | None = None,
    created_before: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
) -> dict:
    """List rendered videos with optional filters.

    Args:
        automation_id: Filter by automation.
        video_type: "slideshow", "ugc", or "greenscreen".
        status: "completed", "processing", or "failed".
        finished: "true" or "false".
        failed: "true" or "false".
        created_after: ISO 8601 timestamp.
        created_before: ISO 8601 timestamp.
        limit: Max results (default 20, max 100).
        offset: Pagination offset.
    """
    params: dict[str, Any] = {}
    for key in [
        "automation_id", "video_type", "status", "finished", "failed",
        "created_after", "created_before", "limit", "offset",
    ]:
        val = locals()[key]
        if val is not None:
            params[key] = val
    return await _request("GET", "/videos", params=params)


@mcp.tool()
async def get_video(video_id: str) -> dict:
    """Get full details for a single video including slideshow images and TikTok publish status.

    Args:
        video_id: The video ID.
    """
    return await _request("GET", f"/videos/{video_id}")


@mcp.tool()
async def get_video_analytics(video_id: str) -> dict:
    """Get TikTok post analytics for a published video (views, likes, comments, shares, bookmarks).

    The video must have been published to TikTok.

    Args:
        video_id: The video ID.
    """
    return await _request("GET", f"/videos/{video_id}/analytics")


@mcp.tool()
async def publish_video_via_automation(
    video_id: str,
    post_mode: str | None = None,
) -> dict:
    """Publish a completed video to TikTok using the automation's saved settings.

    The video must be linked to an automation. For standalone publishing, use publish_to_tiktok instead.

    Args:
        video_id: The video ID (must be completed).
        post_mode: "DIRECT_POST" or "MEDIA_UPLOAD" (TikTok draft). Defaults to automation's setting.
    """
    body: dict[str, Any] = {}
    if post_mode:
        body["post_mode"] = post_mode
    return await _request("POST", f"/videos/{video_id}/publish", json_body=body)


# ===========================================================================
# TIKTOK
# ===========================================================================


@mcp.tool()
async def publish_to_tiktok(
    video_id: str,
    tiktok_account_id: str,
    upload_type: str | None = None,
    caption: str | None = None,
    description: str | None = None,
    post_mode: str | None = None,
    visibility: str | None = None,
    allow_comments: bool | None = None,
    allow_duet: bool | None = None,
    allow_stitch: bool | None = None,
    auto_music: bool | None = None,
    disclose_video_content: bool | None = None,
    disclose_brand_organic: bool | None = None,
    disclose_branded_content: bool | None = None,
    slideshow_image_urls: list[str] | None = None,
) -> dict:
    """Publish a completed video to TikTok with all settings provided directly (no automation needed).

    Note: TikTok limits 6 publishes per 24 hours. Use MEDIA_UPLOAD (draft) to avoid this.

    Args:
        video_id: The video to publish (must be completed).
        tiktok_account_id: Target TikTok account.
        upload_type: "slides" (photo post, default) or "video" (.mp4).
        caption: Post title/caption (max 89 chars for slideshows).
        description: Description/hashtags (max 4000 chars).
        post_mode: "DIRECT_POST" (default) or "MEDIA_UPLOAD" (draft).
        visibility: "PUBLIC_TO_EVERYONE", "SELF_ONLY", "MUTUAL_FOLLOW_FRIENDS", "FOLLOWER_OF_CREATOR".
        allow_comments: Allow comments (default true).
        allow_duet: Allow duets (default true).
        allow_stitch: Allow stitches (default true).
        auto_music: Let TikTok add trending music (default true, slideshows only).
        disclose_video_content: Disclose video content.
        disclose_brand_organic: Disclose brand organic.
        disclose_branded_content: Disclose branded content.
        slideshow_image_urls: Override slideshow images with custom URLs.
    """
    body: dict[str, Any] = {
        "video_id": video_id,
        "tiktok_account_id": tiktok_account_id,
    }
    for key in [
        "upload_type", "caption", "description", "post_mode", "visibility",
        "allow_comments", "allow_duet", "allow_stitch", "auto_music",
        "disclose_video_content", "disclose_brand_organic",
        "disclose_branded_content", "slideshow_image_urls",
    ]:
        val = locals()[key]
        if val is not None:
            body[key] = val
    return await _request("POST", "/tiktok/publish", json_body=body)


@mcp.tool()
async def list_tiktok_accounts() -> dict:
    """List TikTok accounts connected via OAuth."""
    return await _request("GET", "/tiktok/accounts")


@mcp.tool()
async def list_tiktok_posts(
    timeframe: str | None = None,
    sort: str | None = None,
    tiktok_account_id: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
) -> dict:
    """List TikTok posts with engagement metrics and aggregated statistics.

    Args:
        timeframe: 7, 30, 90, or "all" (default 30).
        sort: "recent", "views", "likes", "shares", "comments", "bookmarks".
        tiktok_account_id: Filter by account.
        limit: Default 20, max 200.
        offset: Pagination offset.
    """
    params: dict[str, Any] = {}
    for key in ["timeframe", "sort", "tiktok_account_id", "limit", "offset"]:
        val = locals()[key]
        if val is not None:
            params[key] = val
    return await _request("GET", "/tiktok/posts", params=params)


# ===========================================================================
# COLLECTIONS
# ===========================================================================


@mcp.tool()
async def list_collections() -> dict:
    """List all image collections belonging to the authenticated user."""
    return await _request("GET", "/collections")


@mcp.tool()
async def get_collection_images(
    collection_id: int,
    limit: int | None = None,
    offset: int | None = None,
) -> dict:
    """Get images in a collection, paginated.

    Args:
        collection_id: The collection ID.
        limit: Max results (default 100, max 100).
        offset: Pagination offset.
    """
    params: dict[str, Any] = {}
    if limit is not None:
        params["limit"] = limit
    if offset is not None:
        params["offset"] = offset
    return await _request("GET", f"/collections/{collection_id}/images", params=params)


# ===========================================================================
# SLIDESHOW LIBRARY
# ===========================================================================


@mcp.tool()
async def list_library_niches() -> dict:
    """List all available niches in the slideshow library with profile counts."""
    return await _request("GET", "/library/niches")


@mcp.tool()
async def search_library(
    q: str | None = None,
    niche: str | None = None,
    product_medium: str | None = None,
    region: str | None = None,
    audience_region: str | None = None,
    sort: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
) -> dict:
    """Search real TikTok slideshow profiles for inspiration and competitive research.

    At least one filter is required.

    Args:
        q: Text search across slide content.
        niche: Filter by niche (e.g. "fitness").
        product_medium: Filter by product type.
        region: Account region code (e.g. "US").
        audience_region: Audience country code (e.g. "US").
        sort: "followers" (default) or "recent".
        limit: Default 3, max 3.
        offset: Pagination offset.
    """
    params: dict[str, Any] = {}
    for key in [
        "q", "niche", "product_medium", "region",
        "audience_region", "sort", "limit", "offset",
    ]:
        val = locals()[key]
        if val is not None:
            params[key] = val
    return await _request("GET", "/library", params=params)


@mcp.tool()
async def get_library_profile(profile_id: int) -> dict:
    """Get full details of a slideshow library profile including all slideshow images.

    Args:
        profile_id: The profile ID.
    """
    return await _request("GET", f"/library/profiles/{profile_id}")


# ===========================================================================
# PINTEREST
# ===========================================================================


@mcp.tool()
async def search_pinterest(
    q: str,
    cursor: str | None = None,
) -> dict:
    """Search Pinterest for high-resolution images to use in slideshows.

    Paginated up to 5 pages per search query.

    Args:
        q: Search query (e.g. "aesthetic coffee").
        cursor: Pagination cursor from a previous response.
    """
    params: dict[str, Any] = {"q": q}
    if cursor:
        params["cursor"] = cursor
    return await _request("GET", "/pinterest/search", params=params)


# ===========================================================================
# Entry point
# ===========================================================================


def main():
    """Run the ReelFarm MCP server."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
