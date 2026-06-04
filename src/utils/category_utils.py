from typing import Literal
from ..scraping.llm.llm_scraper import get_property_with_llm

JobCategory = Literal[
    'Data',
    'Mobile',
    'QA',
    'Security',
    'UX/UI',
    'Manager',
    'DevOps',
    'Embedded',
    'Backend',
    'Frontend',
    'Fullstack',
    'AI',
    'Support',
    'Game',
    'Auto',
    'Other'
]

job_category_list = list(JobCategory.__args__)

def get_category_helper(title: str, tech_stack: str, full_offer: str, breadcrumbs: str = '') -> JobCategory:
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
    if 'business analyst' in title or 'manager' in title or 'pmo' in title or 'product owner' in title:
        return 'Manager'
    if 'devops' in title or 'automation' in title:
        return 'DevOps'
    if 'embedded' in title:
        return 'Embedded'
    if 'backend' in title or 'back-end' in title:
        return 'Backend'
    if 'frontend' in title or 'front-end' in title:
        return 'Frontend'
    if 'fullstack' in title or 'full-stack' in title or 'full stack' in title:
        return 'Fullstack'
    if 'ai' in title or 'ml' in title:
        return 'AI'
    if 'support' in title or 'wsparc' in title or 'konsult' in title or 'consultant' in title or 'sre' in title: 
        return 'Support'
    if 'game' in title:
        return 'Game'
    if 'auto' in title:
        return 'Auto'

    if breadcrumbs:
        return get_category_helper(breadcrumbs.lower(), tech_stack, full_offer)

    llm_result = get_property_with_llm(
        full_offer,
        'the job category',
        ', '.join(job_category_list)
    )
    if llm_result and llm_result in job_category_list:
        return llm_result

    return 'Other'

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
