from bs4 import BeautifulSoup
import re

from ...utils.salary_utils import (
    get_salary_type,
    get_salary
)


def get_category_helper(title: str, tech_stack: str) -> str:
    if not title:
        title = ''
    title = title.lower()
    tech_stack = tech_stack.lower()

    if 'data' in title or 'danych' in title or 'danymi' in title:
        return 'Data'
    if 'android' in title or 'mobil' in title or 'react native' in title or 'flutter' in title:
        return 'Mobile'
    if 'test' in title or 'qa' in title:
        return 'QA'
    if 'cyber' in title or 'security' in title or 'bezpieczeństwa' in title:
        return 'Security'
    if 'ux' in title or  'ui' in title:
        return 'UX/UI'
    if 'ruby' in title:
        return 'Ruby'
    if 'business analyst' in title or 'manager' in title or 'pmo' in title or 'product owner' in title:
        return 'Manager'
    if 'devops' in title or 'automation' in title:
        return 'DevOps'
    if 'embedded' in title:
        return 'Embedded'
    if 'backend' in title or 'back-end' in title: # In what ??
        return 'Backend'
    if 'frontend' in title or 'front-end' in title:  # In what ??
        return 'Frontend'
    if 'fullstack' in title or 'full-stack' in title or 'full stack' in title:  # In what ??
        return 'Fullstack'
    if 'ai' in title:
        return 'AI'
    if 'support' in title or 'wsparc' in title or 'konsult' in title or 'consultant' in title or 'sre' in title: 
        return 'Support'

    return ''

def get_frontend_subcategory(title: str, tech_stack: str) -> str:
    title_stack = title.lower() + ' ' + tech_stack.lower()

    sub_category = []
    if 'angular' in title_stack or 'ngrx' in title_stack:
        sub_category.append('Angular')
    if 'react' in title_stack:
        sub_category.append('React')
    if 'react native' in title_stack:
        sub_category.append('React Native')
    if 'nestjs' in title_stack:
        sub_category.append('NestJS')
    if 'next' in title_stack:
        sub_category.append('Next')
    if 'vite' in title_stack:
        sub_category.append('Vite')
    if 'vue' in title_stack:
        sub_category.append('Vue')
    if 'php' in title_stack or 'laravel' in title_stack:
        sub_category.append('PHP')

    return ', '.join(sub_category)

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
