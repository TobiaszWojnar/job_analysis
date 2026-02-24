from bs4 import BeautifulSoup
import re
from .base_strategy import BaseJobStrategy
from .strategy_helper import get_category_helper, get_text_helper, get_salary_type_helper, get_salary_helper, get_years_of_experience_helper
from ...utils.salary_utils import get_salary as get_salary_util, get_salary_type as get_salary_type_util

class JustJoinItStrategy(BaseJobStrategy):
    def get_title(self, soup: BeautifulSoup) -> str:
        return get_text_helper(soup.find('h1'))

    def get_company(self, soup: BeautifulSoup) -> str:
        company_h2 = soup.find('h2')
        if company_h2:
            return get_text_helper(company_h2)
        return ''

    def get_company_link(self, soup: BeautifulSoup) -> str: # TODO implement
        company_h2 = soup.find('h2')
        if company_h2:
            parent_link = company_h2.find_parent('a')
            if parent_link and parent_link.get('href'):
                return parent_link.get('href')
        return ''

    def get_company_description(self, soup: BeautifulSoup) -> str: # TODO implement
        return ''

    def get_category(self, soup: BeautifulSoup) -> str:
        # Try breadcrumbs first as they are very reliable on JustJoinIT
        breadcrumbs = soup.find('nav', class_=re.compile('Breadcrumbs', re.I)) or soup.find('ol', class_=re.compile('Breadcrumbs', re.I))
        if breadcrumbs:
            links = breadcrumbs.find_all('a')
            for link in links:
                href = link.get('href', '')
                if '/job-offers/all-locations/' in href:
                    cat_text = get_text_helper(link).strip()
                    if cat_text and cat_text.lower() not in ['all offers', 'wszystkie oferty']:
                        return cat_text

        title = self.get_title(soup)
        tech_stack = self.get_tech_stack(soup)
        cat = get_category_helper(title, tech_stack)
        return cat

    def get_tech_stack(self, soup: BeautifulSoup) -> str:
        # Find all h4 tags that are siblings or nested in a stack with specific MUI classes
        # or follow the "Tech stack" heading.
        tech_tags = soup.find_all('h4', class_=re.compile('mui-1i3ah26|mui-pc1kzi', re.IGNORECASE))
        if not tech_tags:
             # Try finding by section
             header = soup.find(string=re.compile("Tech stack", re.IGNORECASE))
             if header:
                 section = header.find_parent('div')
                 if section:
                     tech_tags = section.find_all('h4')
        
        stack = []
        for tag in tech_tags:
            text = get_text_helper(tag).strip()
            if text:
                # Remove extra newlines/spaces within the text
                text = ' '.join(text.split())
                stack.append(text)
        
        return ', '.join(stack) if stack else ''

    def get_location(self, soup: BeautifulSoup) -> str:
        # Find all paths that match the location pin icon
        location_icons = soup.find_all('path', d=re.compile(r'^M12 2C16\.2 2 20 5\.22', re.IGNORECASE))
        for icon in location_icons:
            # Check container div or parent div
            container = icon.find_parent('div', class_='mui-bva120') or icon.find_parent('div')
            if container:
                text = get_text_helper(container).strip()
                # Clean up ZWSP and check if it looks like a valid location (has comma or city name)
                text = text.replace('\u200b', '').replace('\xa0', ' ')
                if text and ',' in text and 'Search:' not in text and 'Job title' not in text:
                    return text
        
        # Fallback to address-like pattern in mui-bva120
        possible_locs = soup.find_all('div', class_='mui-bva120')
        for loc in possible_locs:
            text = get_text_helper(loc).strip().replace('\u200b', '').replace('\xa0', ' ')
            if text and ',' in text and 'Search:' not in text and 'Job title' not in text:
                 return text
        return ''

    def get_location_type(self, soup: BeautifulSoup) -> str:
        text = soup.get_text().lower()
        if 'remote' in text or 'zdalna' in text:
            return 'remote'
        if 'hybrid' in text or 'hybrydowa' in text:
            return 'hybrid'
        return 'office'

    def get_salary(self, soup: BeautifulSoup) -> str:
        salary_h6 = soup.find('h6', class_=re.compile('mui-3q7vsr', re.IGNORECASE))
        if salary_h6:
            text = get_text_helper(salary_h6)
            text = ' '.join(text.split()) # Normalize whitespace
            return get_salary_util(text)
        
        return ''

    def get_salary_type(self, soup: BeautifulSoup) -> str:
        # Salary type info is often in a span next to the salary h6
        salary_h6 = soup.find('h6', class_=re.compile('mui-3q7vsr', re.IGNORECASE))
        if salary_h6:
            # Check siblings or siblings of parent
            parent = salary_h6.parent
            if parent:
                # Often it's in a span or div following the h6
                info = parent.get_text()
                return get_salary_type_util(info)
        return ''

    def get_years_of_experience(self, soup: BeautifulSoup) -> str:
        # Look for Junior/Mid/Senior/Expert in mui-1lxw2mb tags
        # These tags also contain "Full-time", "B2B", "Remote" etc.
        exp_tags = soup.find_all('div', class_=re.compile('mui-1lxw2mb', re.IGNORECASE))
        for tag in exp_tags:
            text = get_text_helper(tag).strip()
            if text in ['Junior', 'Mid', 'Senior', 'Expert']:
                return text
        
        return get_years_of_experience_helper(soup)

    def get_responsibilities(self, soup: BeautifulSoup) -> str:
        # Often under "Responsibilities" or "Zakres obowiązków"
        section = soup.find(string=re.compile(r"Responsibilities|Zakres obowiązków", re.IGNORECASE))
        if section:
            parent = section.find_parent()
            next_list = parent.find_next('ul') if parent else None
            if next_list:
                return get_text_helper(next_list)
        return ''

    def get_requirements(self, soup: BeautifulSoup) -> str:
        # Often under "Requirements" or "Wymagania"
        section = soup.find(string=re.compile(r"Requirements|Wymagania", re.IGNORECASE))
        if section:
            parent = section.find_parent()
            next_list = parent.find_next('ul') if parent else None
            if next_list:
                return get_text_helper(next_list)
        return ''

    def get_benefits(self, soup: BeautifulSoup) -> str:
        # Often under "What we offer" or "Co oferujemy"
        section = soup.find(string=re.compile(r"offer|oferujemy|benefits", re.IGNORECASE))
        if section:
            parent = section.find_parent()
            next_list = parent.find_next('ul') if parent else None
            if next_list:
                return get_text_helper(next_list)
        return ''

    def get_full_offer(self, soup: BeautifulSoup) -> str:
        return get_text_helper(soup)