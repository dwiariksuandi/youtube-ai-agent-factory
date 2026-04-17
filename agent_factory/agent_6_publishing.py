"""
agent_6_publishing.py – Publishing Agent (YouTube upload via Data API v3)
"""

from config import app_config
from typing import List, Dict, Optional
import os
import json
import pickle
import googleapiclient.discovery
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.http import MediaFileUpload
from pathlib import Path
from rich.console import Console
from langsmith import traceable

console = Console()


SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
]


def authenticate_youtube() -> googleapiclient.discovery.Resource:
    """
    Authenticate to YouTube API v3.
    """
    credentials = None
    token_path = app_config.youtube_token_file

    if os.path.exists(token_path):
        with open(token_path, "rb") as f:
            credentials = pickle.load(f)

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            secrets_path = app_config.youtube_client_secrets_file
            if not os.path.exists(secrets_path):
                console.log("[red]❌ client_secret.json not found")
                raise FileNotFoundError(secrets_path)

            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                secrets_path,
                SCOPES,
            )
            credentials = flow.run_local_server(port=0)

        with open(token_path, "wb") as f:
            pickle.dump(credentials, f)

    return googleapiclient.discovery.build("youtube", "v3", credentials=credentials)


class VideoMetadata:
    def __init__(self, file_path: str, file_stem: str, kind: str, title: str, description: str, tags: List[str], thumbnail_path: str):
        self.file_path = file_path
        self.file_stem = file_stem
        self.kind = kind
        self.title = title
        self.description = description
        self.tags = tags
        self.thumbnail_path = thumbnail_path

    def build_snippet(self) -> Dict:
        return {
            "title": self.title,
            "description": self.description,
            "tags": self.tags,
            "categoryId": app_config.youtube_category_id,
        }

    def build_status(self) -> Dict:
        return {
            "privacyStatus": app_config.youtube_privacy,
        }


class PublishingAgent:
    def __init__(
        self,
        videos_dir: str = "",
        thumbnails_dir: str = "",
    ):
        self.videos_long_dir = os.path.join(videos_dir or app_config.youtube_videos_dir, "long")
        self.videos_shorts_dir = os.path.join(videos_dir or app_config.youtube_videos_dir, "shorts")

        self.thumbnails_dir = thumbnails_dir or app_config.youtube_thumbnails_dir

        self.youtube = authenticate_youtube()

    def discover_video_files(self) -> List[Dict]:
        """
        Cari video: veo_long_*.mp4, veo_shorts_*.mp4.
        """
        p_long = Path(self.videos_long_dir)
        p_shorts = Path(self.videos_shorts_dir)
        result = []

        # LONG
        for f in p_long.glob("veo_long_*.mp4"):
            stem = f.stem
            topic_id = stem.replace("veo_long_", "")
            result.append({
                "path": str(f),
                "kind": "long",
                "topic_id": topic_id,
                "file_stem": stem,
                "aspect": "16:9",
            })

        # SHORTS
        for f in p_shorts.glob("veo_shorts_*.mp4"):
            stem = f.stem
            topic_id = stem.replace("veo_shorts_", "")
            result.append({
                "path": str(f),
                "kind": "shorts",
                "topic_id": topic_id,
                "file_stem": stem,
                "aspect": "9:16",
            })

        console.log(f"[cyan]📁 Found {len(result)} video files")
        return result

    def find_thumbnail_for_topic_id(self, topic_id: str, kind: str) -> Optional[str]:
        """
        thumb_long_veo_long_001.jpg
        """
        base = f"thumb_{kind}_veo_{kind}_{topic_id}.jpg"
        p = Path(self.thumbnails_dir) / base
        if p.exists():
            return str(p)
        return None

    def build_video_metadata(self, video_info: Dict) -> Optional[VideoMetadata]:
        topic_id = video_info["topic_id"]
        kind = video_info["kind"]
        video_path = video_info["path"]

        title = f"AI Agent Factory: {topic_id}"
        desc = (
            "Video otomatis dibuat oleh AI Agent Factory (YouTube Automation + AI).\n\n"
            "Belajar AI, Automation, dan Productivity secara otomatis.\n"
            "Saksikan bagaimana 100% sistem AI menghasilkan video ini."
        )
        tags = [
            "AI",
            "Automation",
            "Productivity",
            "YouTube",
            "AI Agent",
            "Business Automation",
        ]

        thumbnail_path = self.find_thumbnail_for_topic_id(topic_id, kind)
        if not thumbnail_path:
            console.log(f"[yellow]⚠️ No thumbnail for {topic_id}")

        return VideoMetadata(
            file_path=video_path,
            file_stem=video_info["file_stem"],
            kind=kind,
            title=title,
            description=desc,
            tags=tags,
            thumbnail_path=thumbnail_path,
        )

    def upload_video(
        self,
        video_path: str,
        metadata: VideoMetadata,
        is_shorts: bool = False,
    ) -> Optional[str]:
        """
        Upload video ke YouTube.
        """
        body = {
            "snippet": metadata.build_snippet(),
            "status": metadata.build_status(),
        }

        if is_shorts:
            body["statisticsVerifiable"] = False

        media = MediaFileUpload(video_path, chunksize=-1, resumable=True)

        try:
            request = self.youtube.videos().insert(
                part="snippet,status",
                body=body,
                media_body=media,
            )
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    console.log(f"[blue]📤 {metadata.title} progress: {status.progress()}")

            video_id = response.get("id")
            if video_id:
                console.log(f"[green]✅ Video uploaded: {video_id}")
            return video_id

        except Exception as e:
            console.log(f"[red]❌ Upload failed: {e}")
            return None

    def upload_thumbnail(self, video_id: str, thumb_path: str) -> bool:
        """
        Upload thumbnail ke video.
        """
        if not os.path.exists(thumb_path):
            console.log(f"[yellow]⚠️ Thumbnail not found: {thumb_path}")
            return False

        media = MediaFileUpload(thumb_path)

        try:
            request = self.youtube.thumbnails().set(videoId=video_id, media_body=media)
            request.execute()
            console.log(f"[green]✅ Thumbnail uploaded to {video_id}")
            return True
        except Exception as e:
            console.log(f"[red]❌ Thumbnail upload failed: {e}")
            return False

    def process_single_video(self, video_info: Dict) -> Optional[str]:
        metadata = self.build_video_metadata(video_info)
        if not metadata:
            return None

        is_shorts = (video_info["kind"] == "shorts")
        console.log(f"[cyan]📤 Uploading: {metadata.title}")

        video_id = self.upload_video(metadata.file_path, metadata, is_shorts=is_shorts)
        if video_id and metadata.thumbnail_path:
            self.upload_thumbnail(video_id, metadata.thumbnail_path)

        return video_id

    def run(self) -> List[str]:
        console.rule("[bold magenta]AGENT 6 – PUBLISHING AGENT (YouTube Upload)")
        video_ids = []

        videos = self.discover_video_files()
        if not videos:
            console.log("[yellow]⚠️ No video files to upload")
            return video_ids

        for info in videos:
            video_id = self.process_single_video(info)
            if video_id:
                video_ids.append(video_id)

        console.log(f"[green]✅ Agent 6 done: {len(video_ids)} video(s) uploaded.")
        return video_ids


if __name__ == "__main__":
    agent = PublishingAgent(
        videos_dir="agent_factory/videos",
        thumbnails_dir="agent_factory/thumbnails",
    )
    agent.run()
