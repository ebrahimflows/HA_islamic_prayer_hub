"""Constants for Prayer Hub."""

DOMAIN = "prayer_hub"
PLATFORMS = ["sensor"]

CONF_LUPT_ENTITY = "lupt_entity"
CONF_TV_ENTITY = "tv_entity"
CONF_TABLET_SCREEN_ENTITY = "tablet_screen_entity"
CONF_FULLY_KIOSK_DEVICE_ID = "fully_kiosk_device_id"
CONF_HOME_ASSISTANT_URL = "home_assistant_url"
CONF_DASHBOARD_RETURN_PATH = "dashboard_return_path"
CONF_LIGHT_ENTITIES = "light_entities"
CONF_VIDEO_ID = "video_id"
CONF_FAJR_VIDEO_ID = "fajr_video_id"
CONF_VOLUME = "volume"
CONF_COUNTDOWN = "countdown"
CONF_FALLBACK_SECONDS = "fallback_seconds"
CONF_AUTOMATIC = "automatic"
CONF_FINISH_TOKEN = "finish_token"

SERVICE_START = "start"
SERVICE_STOP = "stop"

DEFAULT_VIDEO_ID = "SI4CScs4D2Q"
DEFAULT_FAJR_VIDEO_ID = "Yazp1Nz-eBE"
DEFAULT_VOLUME = 85
DEFAULT_COUNTDOWN = 3
DEFAULT_FALLBACK_SECONDS = 420
DEFAULT_DASHBOARD_PATH = "/"

PRAYER_STATES = {
    "Fajr": "Fajr",
    "Zuhr": "Dhuhr",
    "Asr": "Asr",
    "Maghrib": "Maghrib",
    "Ishā": "Isha",
    "Isha": "Isha",
}

NEXT_ATTRIBUTE_MAP = {
    "Fajr": "next_fajr",
    "Dhuhr": "next_zuhr",
    "Asr": "next_asr",
    "Maghrib": "next_maghrib",
    "Isha": "next_ishā",
}
