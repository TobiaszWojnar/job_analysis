from abc import ABC, abstractmethod
from bs4 import BeautifulSoup

class BaseJobStrategy(ABC):
    @abstractmethod
    def get_title(self, soup: BeautifulSoup) -> str:
        pass

    @abstractmethod
    def get_company(self, soup: BeautifulSoup) -> str:
        pass

    @abstractmethod
    def get_company_link(self, soup: BeautifulSoup) -> str:
        pass

    @abstractmethod
    def get_company_description(self, soup: BeautifulSoup) -> str:
        pass

    @abstractmethod
    def get_category(self, soup: BeautifulSoup) -> str:
        pass

    @abstractmethod
    def get_tech_stack(self, soup: BeautifulSoup) -> str:
        pass

    @abstractmethod
    def get_location(self, soup: BeautifulSoup) -> str:
        pass

    @abstractmethod
    def get_location_type(self, soup: BeautifulSoup) -> str:
        pass

    @abstractmethod
    def get_salary(self, soup: BeautifulSoup) -> str:
        pass

    @abstractmethod
    def get_salary_type(self, soup: BeautifulSoup) -> str:
        pass

    @abstractmethod
    def get_years_of_experience(self, soup: BeautifulSoup) -> str:
        pass

    @abstractmethod
    def get_responsibilities(self, soup: BeautifulSoup) -> str:
        pass

    @abstractmethod
    def get_requirements(self, soup: BeautifulSoup) -> str:
        pass

    @abstractmethod
    def get_benefits(self, soup: BeautifulSoup) -> str:
        pass

    @abstractmethod
    def get_full_offer(self, soup: BeautifulSoup) -> str:
        pass
