import cloudinary
import cloudinary.uploader
import cloudinary.utils

from config import CLOUD_NAME, API_KEY, API_SECRET


# Configure Cloudinary
cloudinary.config(
    cloud_name=CLOUD_NAME,
    api_key=API_KEY,
    api_secret=API_SECRET,
    secure=True
)


def upload_video(file_path: str):
    """
    Upload a video to Cloudinary and return useful information.
    """

    result = cloudinary.uploader.upload(
        file_path,
        resource_type="video",
        folder="telegram_videos"
    )

    public_id = result["public_id"]

    # Generate streaming URL
    video_url, _ = cloudinary.utils.cloudinary_url(
        public_id,
        resource_type="video",
        secure=True
    )

    # Generate thumbnail URL
    thumbnail_url, _ = cloudinary.utils.cloudinary_url(
        public_id,
        resource_type="video",
        format="jpg",
        secure=True
    )

    return {
        "public_id": public_id,
        "video_url": video_url,
        "thumbnail_url": thumbnail_url,
        "duration": result.get("duration"),
        "width": result.get("width"),
        "height": result.get("height"),
        "bytes": result.get("bytes"),
        "format": result.get("format"),
        "created_at": result.get("created_at"),
    }
