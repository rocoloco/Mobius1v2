"""
Application constants and default values.

These are compile-time constants. For runtime configuration, see config.py.
"""

# File size limits
MAX_PDF_SIZE_BYTES = 50 * 1024 * 1024  # 50MB
MAX_IMAGE_SIZE_BYTES = 10 * 1024 * 1024  # 10MB

# Allowed MIME types
ALLOWED_PDF_MIME_TYPES = ["application/pdf"]
ALLOWED_IMAGE_MIME_TYPES = ["image/png", "image/jpeg", "image/webp"]

# Compliance scoring
DEFAULT_COMPLIANCE_THRESHOLD = 0.80  # 80%
DEFAULT_TEMPLATE_THRESHOLD = 0.95  # 95%
CATEGORY_WEIGHTS = {
    "colors": 0.30,  # Color compliance is critical for brand recognition
    "typography": 0.25,  # Typography affects readability and brand voice
    "layout": 0.25,  # Layout/composition impacts visual hierarchy
    "logo_usage": 0.20,  # Logo rules (when applicable)
}

# Job management
DEFAULT_MAX_ATTEMPTS = 3
DEFAULT_JOB_EXPIRY_HOURS = 24
DEFAULT_WEBHOOK_RETRY_MAX = 5

# Learning activation
LEARNING_ACTIVATION_THRESHOLD = 50  # feedback count to activate learning

# API
API_VERSION = "v1"
REQUEST_ID_PREFIX = "req_"

# Storage buckets
BRANDS_BUCKET = "brands"
ASSETS_BUCKET = "assets"
