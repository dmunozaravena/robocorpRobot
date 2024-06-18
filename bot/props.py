regex_currency = r'\$\d+(,\d{3})*(\.\d{2})?|\d+ (dollars|USD)'
props = {
    "work_item_path": "devdata/work-items-in/work-items/work-items.json",
    "wait_timeout": 30,
    "img_dir": "img",
    "output_dir": "output",
    "img_filename": "image_{timestamp}.jpg",
    "search_phrase": "document.getElementsByName('q')[0].value='{search_text}';document.forms[0].submit()", # NOQA
    "xpath_elements_li": "//ps-search-filters//ul[contains(@class, 'search-results')]/li", # NOQA
    "xpath_title_news": "xpath:.//h3[@class='promo-title']/a",
    "xpath_description_news": "xpath:.//p[@class='promo-description']",
    "xpath_date_news": "xpath:.//p[@class='promo-timestamp']",
    "xpath_date_news_full": "xpath:.//p[@class='promo-timestamp post-date-time-recent']", # NOQA
    "xpath_img_news": "xpath:.//img[@class='image']",
    "attribute_date": "data-timestamp",
    "attribute_src": "src",
    "order_by_newest": 'name:s',
    "xpath_newest": "//select[@name='s']",
    "xpath_filters": "//span[text()='{filters}']",
    "filter_titles": ["Type", "Topics"],
    "xpath_filter_titles": "//p[text() = '{title}']/..//span[text() = 'See All']",  # NOQA
    "newest": "1",
    "xlsx_filename": "data.xlsx",
    "template_result": {"title": "{title}",
                        "description": "{description}",
                        "timestamp": "{timestamp}",
                        "file_name": "{file_name}",
                        "currency": "{currency}",
                        "counted_phrase": "{counted_phrase}"
                        },
    "cols": ["Title", "Description", "Date", "Image Filename", "$ Found", "Count Phrases"], # NOQA
}
