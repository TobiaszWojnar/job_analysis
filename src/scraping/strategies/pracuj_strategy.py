from bs4 import BeautifulSoup
import re
from .base_strategy import BaseJobStrategy
from .strategy_helper import get_category_helper, get_salary_type_helper, get_text_helper, get_salary_helper, get_years_of_experience_helper

class PracujStrategy(BaseJobStrategy):
    def get_title(self, soup: BeautifulSoup) -> str:
        title = get_text_helper(soup.find('h1', attrs={'data-test': 'text-positionName'}))
        if title:
            return title
        return ''

    def get_company(self, soup: BeautifulSoup) -> str:
        return get_text_helper(soup.find('h2', attrs={'data-test':'text-employerName'}), ['O firmie'])

    def get_company_link(self, soup: BeautifulSoup) -> str:
        employer_profile = soup.find(attrs={'data-test':'section-employer-profile'})
        if employer_profile is None or employer_profile.find('a') is None:
            return ''
        return employer_profile.find('a').get('href')

    def get_company_description(self, soup: BeautifulSoup) -> str:
        about_us = soup.find(attrs={'data-scroll-id': 'about-us-description-1'})
        if about_us is None:
            return ''
        about_us = about_us.find_all('li')
        return ', '.join(get_text_helper(about) for about in about_us)

    def get_category(self, soup: BeautifulSoup) -> str:
        tech_stack = self.get_tech_stack(soup)
        it_specializations = get_text_helper(soup.find(attrs={'data-test': 'it-specializations'}))

        category = get_category_helper(self.get_title(soup), tech_stack)

        if category:
            return category

        if it_specializations:
            return get_category_helper(it_specializations, tech_stack)
        return ''

    def get_tech_stack(self, soup: BeautifulSoup) -> str:
        expected_section = soup.find(attrs={'data-test': 'section-technologies-expected'})
        expected = expected_section.find_all('span') if expected_section else []
        
        optional_section = soup.find(attrs={'data-test': 'section-technologies-optional'})
        optional = optional_section.find_all('span') if optional_section else []

        return ", ".join(get_text_helper(tech) for tech in expected + optional)

    def get_location(self, soup: BeautifulSoup) -> str:
        return get_text_helper(soup.find(attrs={'data-scroll-id': 'workplaces'}))

    def get_location_type(self, soup: BeautifulSoup) -> str:
        return get_text_helper(soup.find(attrs={'data-scroll-id': 'work-modes'}))

    def get_salary(self, soup: BeautifulSoup) -> str:
        return get_salary_helper(soup.find(attrs={'data-test': 'section-salary'}))

    def get_salary_type(self, soup: BeautifulSoup) -> str:
        salary_section = soup.find(attrs={'data-test': 'section-salary'})

        return get_salary_type_helper(salary_section)

    def get_years_of_experience(self, soup: BeautifulSoup) -> str:
        return get_years_of_experience_helper(soup)

    def get_responsibilities(self, soup: BeautifulSoup) -> str:
        responsibilities = soup.find(attrs={'data-test':'section-responsibilities'}).find_all('li')
        return ", ".join(get_text_helper(responsibility) for responsibility in responsibilities)

    def get_requirements(self, soup: BeautifulSoup) -> str:
        requirements = soup.find(attrs={'data-test':'section-requirements'}).find_all('li')
        return ", ".join(get_text_helper(requirement) for requirement in requirements)

    def get_benefits(self, soup: BeautifulSoup) -> str:
        benefits = soup.find_all(attrs={'data-test':'list-item-benefit'})

        offered_section = soup.find(attrs={'data-test':'section-offered'})
        offered = offered_section.find_all('li') if offered_section else []

        trainings_section = soup.find(attrs={'data-test':'section-training-space'})
        trainings = trainings_section.find_all('li') if trainings_section else []
        return ", ".join(get_text_helper(benefit) for benefit in benefits+offered)

    def get_full_offer(self, soup: BeautifulSoup) -> str:
        return get_text_helper(soup.find(id="offer-details").find('div'))

