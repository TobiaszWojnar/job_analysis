from bs4 import BeautifulSoup
import re

from ...utils.salary_utils import (
    get_salary_type,
    get_salary
)

def get_salary_type_helper(salary_section: BeautifulSoup) -> str:
    if not salary_section:
        return ''

    salary_text = get_text_helper(salary_section)

    return get_salary_type(salary_text)


def get_text_helper(node: BeautifulSoup, replace_strs: list[str] = []) -> str:
    if not node:
        return ''
    text = node.get_text(strip=True, separator=' ').replace('\xa0', ' ').replace('–','-')

    for replace_str in replace_strs:
        text = text.replace(replace_str, '')
    return text

def get_years_of_experience_helper(node: BeautifulSoup) -> str:
    text = node.get_text()
    matches_pl = re.findall(r'(?:\+|\()?\s*(\d+(?:\.\d+)?(?:-\d+(?:\.\d+)?)?)\s*\+?\s+lat', text)
    matches_en = re.findall(r'(?:\+|\()?\s*(\d+(?:\.\d+)?(?:-\d+(?:\.\d+)?)?)\s*\+?\s+year', text)
    return ", ".join(matches_pl + matches_en)


def get_salary_helper(salary_section: BeautifulSoup) -> str:
    salary_text = get_text_helper(salary_section)
    return get_salary(salary_text)
