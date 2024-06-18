import os
import requests
import re
from datetime import (datetime,
                      timedelta,
                      )

from .props import (props,
                    regex_currency,
                    )


def update_result(template, **kwargs) -> dict:
    """Update template dict with corect data"""
    copy_template = template.copy()
    for key, value in copy_template.items():
        if isinstance(value, str):
            copy_template[key] = value.format(**kwargs)

    return copy_template


def image_filename(timestamp) -> str:
    """Return image filename"""

    return props['img_filename'].format(timestamp=timestamp)


def check_download_dir(formatted_date, logger) -> str:
    """Checks if images directory exists, if not then create it"""
    output_dir = props['output_dir']
    img_dir = props['img_dir']    
    final_directory = f'{output_dir}/{formatted_date}/{img_dir}'
    if not os.path.exists(final_directory):
        os.makedirs(final_directory)
        logger.info(f"Directory '{final_directory}' created successfully.")
    else:
        logger.info(f"Directory '{final_directory}' already exists.")

    return final_directory


def check_exists_output_dir(logger) -> None:
    logger.info('Creating output directory...')
    try:
        output_dir = props['output_dir']
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            logger.info(f"Directory '{output_dir}' created successfully.")
        else:
            logger.info(f"Directory '{output_dir}' already exists.")
    except Exception as e:
        logger.info(f'Failed while try to create directory {output_dir}: {e}')
      
  
def download_image(url, dir, filename, retry=3, **kwargs) -> bool:
    """Download image to local path"""
    downloaded = False
    response = requests.get(url)
    if response.status_code == 200:
        with open(f'{dir}/{filename}', 'wb') as f:
            f.write(response.content)
        downloaded = True
        logger = kwargs.get('logger')
        logger.info(f"Image downloaded successfully as {filename}")
    else:
        logger.info(f"Failed to download image from {url}, retryng")
        retry -= 1
        if retry == 0:
            logger.info("Max retries for download image {url} reached")
        else:
            return download_image(url, dir, filename, retry)

    return downloaded


def count_phrase(title, description, search_phrase) -> int:
    """Count how many time is repeated search phrase"""
    title_lower = title.lower()
    description_lower = description.lower()
    search_phrase_lower = search_phrase.lower()
    title_count = title_lower.count(search_phrase_lower)
    description_count = description_lower.count(search_phrase_lower)

    return title_count + description_count


def check_currency(title, description) -> bool:
    found = False
    regex = re.compile(regex_currency, re.IGNORECASE)
    if regex.search(title) or regex.search(description):
        found = True

    return found


def check_limit_date(timestamp, month=1) -> bool:
    """Check if news datetime is lower to max datetime"""
    skip = False
    if month == 0:
        month = 1
    skip_days = month * 30
    timestamp_datetime = datetime.fromtimestamp(int(timestamp) / 1000)
    print(timestamp_datetime)
    print(datetime.now() - timedelta(days=skip_days))
    if timestamp_datetime < datetime.now() - timedelta(days=skip_days):
        skip = True

    return skip


def check_init_params(url, search_phrase, logger) -> bool:
    logger.info("validationg inputs params")
    is_valid = True
    if not isinstance(url, str) or not re.match(r'https?://\S+\.\S+', url):
        is_valid = False
        logger.error(f"Invalid URL {url}")
    if not isinstance(search_phrase, str) or not search_phrase.strip():
        logger.error(f"Invalid search phrase {search_phrase}")
        is_valid = False
    return is_valid
