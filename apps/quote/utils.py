import base64
import logging

logger = logging.getLogger(__name__)

ALLOWED_MIME_TYPES = {'image/jpeg', 'image/png', 'image/webp'}
MAX_FILES = 5
MAX_FILE_SIZE = 4 * 1024 * 1024  # 4 MB


def files_to_base64(files_list) -> list:
    """
    Convert a list of InMemoryUploadedFile objects to base64 dicts.

    Returns a list of {"data": "<base64 string>", "media_type": "image/jpeg"}.
    - Maximum 5 files (extras are skipped with a warning)
    - Maximum 4 MB per file (oversized files skipped)
    - Allowed MIME types: image/jpeg, image/png, image/webp
      (validated via content_type, then optionally via python-magic)
    """
    result = []

    if len(files_list) > MAX_FILES:
        logger.warning(
            'files_to_base64: received %d files, processing only first %d',
            len(files_list),
            MAX_FILES,
        )

    for uploaded_file in files_list[:MAX_FILES]:
        # Size check
        if uploaded_file.size > MAX_FILE_SIZE:
            logger.warning(
                'files_to_base64: skipping %s — size %d bytes exceeds 4 MB limit',
                uploaded_file.name,
                uploaded_file.size,
            )
            continue

        # MIME check — use Django's content_type first (set by browser on upload)
        mime = (uploaded_file.content_type or '').lower().split(';')[0].strip()

        # Optionally validate with python-magic for extra security
        try:
            import magic

            uploaded_file.seek(0)
            header = uploaded_file.read(2048)
            uploaded_file.seek(0)
            detected = magic.from_buffer(header, mime=True)
            if detected not in ALLOWED_MIME_TYPES:
                logger.warning(
                    'files_to_base64: skipping %s — magic detected type %s not allowed',
                    uploaded_file.name,
                    detected,
                )
                continue
            mime = detected  # trust magic over browser
        except (ImportError, Exception):
            # python-magic not available or failed — fall back to content_type
            if mime not in ALLOWED_MIME_TYPES:
                logger.warning(
                    'files_to_base64: skipping %s — content_type %s not allowed',
                    uploaded_file.name,
                    mime,
                )
                continue

        uploaded_file.seek(0)
        data = base64.b64encode(uploaded_file.read()).decode('ascii')
        result.append({'data': data, 'media_type': mime})

    return result
