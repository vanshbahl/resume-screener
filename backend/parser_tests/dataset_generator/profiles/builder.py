import random
from faker import Faker
from typing import Dict, Any, List
from ..data import pools

class ResumeProfileBuilder:
    def __init__(self, seed: int = None):
        if seed is not None:
            Faker.seed(seed)
            random.seed(seed)
        self.fake = Faker(['en_US', 'en_IN', 'en_GB'])
        
    def generate_profile(self, **kwargs) -> Dict[str, Any]:
        """Generates a complete, structured fake resume profile."""
        industry = kwargs.get('industry', random.choice(pools.INDUSTRIES))
        exp_level = kwargs.get('experience', random.choice(pools.EXPERIENCE_LEVELS))
        country = kwargs.get('country', random.choice(pools.COUNTRIES))
        
        # Decide structural flags based on kwargs or random
        has_summary = kwargs.get('has_summary', random.random() > 0.1)  # 90% chance
        has_projects = kwargs.get('has_projects', exp_level in ["No experience", "Internship", "0-2 years"] or random.random() > 0.3)
        has_experience = kwargs.get('has_experience', exp_level != "No experience")
        
        skills_count = random.randint(5, 12) if kwargs.get('many_skills', False) else random.randint(3, 8)
        
        profile = {
            "metadata": {
                "industry": industry,
                "experience_level": exp_level,
                "country": country,
                "has_summary": has_summary,
                "has_projects": has_projects,
                "has_experience": has_experience,
            },
            "personal_info": self._generate_personal_info(country),
            "summary": self.fake.paragraph(nb_sentences=3) if has_summary else None,
            "skills": self._generate_skills(skills_count),
            "education": self._generate_education(exp_level),
            "experience": self._generate_experience(exp_level, industry) if has_experience else [],
            "projects": self._generate_projects(industry) if has_projects else []
        }
        return profile
        
    def _generate_personal_info(self, country: str) -> Dict[str, Any]:
        # Switch Faker locale based on country if possible, else default
        fake = self.fake
        if country == "India":
            fake = Faker('en_IN')
            
        first_name = fake.first_name()
        last_name = fake.last_name()
        name = f"{first_name} {last_name}"
        
        # Formats
        email = f"{first_name.lower()}.{last_name.lower()}@{fake.free_email_domain()}"
        phone = fake.phone_number()
        location = f"{fake.city()}, {country}"
        
        github = f"github.com/{first_name.lower()}{random.randint(1,99)}" if random.random() > 0.3 else None
        linkedin = f"linkedin.com/in/{first_name.lower()}{last_name.lower()}" if random.random() > 0.1 else None
        portfolio = f"{first_name.lower()}{last_name.lower()}.dev" if random.random() > 0.7 else None
        
        return {
            "name": name,
            "email": email,
            "phone": phone,
            "location": location,
            "github": github,
            "linkedin": linkedin,
            "portfolio": portfolio
        }
        
    def _generate_skills(self, count: int) -> Dict[str, List[str]]:
        langs = random.sample(pools.TECH_STACK['languages'], min(count, len(pools.TECH_STACK['languages'])))
        frameworks = random.sample(pools.TECH_STACK['frameworks'], min(count-1, len(pools.TECH_STACK['frameworks'])))
        tools = random.sample(pools.TECH_STACK['tools'], min(count-2, len(pools.TECH_STACK['tools'])))
        
        return {
            "languages": langs,
            "frameworks": frameworks,
            "tools": tools,
            "all": langs + frameworks + tools
        }
        
    def _generate_education(self, exp_level: str) -> List[Dict[str, Any]]:
        edu = []
        edu_count = 1 if exp_level in ["5-10 years", "10-20 years"] else random.randint(1, 2)
        
        for _ in range(edu_count):
            edu.append({
                "institution": random.choice(pools.UNIVERSITIES),
                "degree": random.choice(pools.DEGREES),
                "graduation_year": str(random.randint(2015, 2026)),
                "cgpa": f"{random.uniform(3.0, 4.0):.2f}" if random.random() > 0.5 else None
            })
        return edu
        
    def _generate_experience(self, exp_level: str, industry: str) -> List[Dict[str, Any]]:
        count_map = {
            "Internship": 1,
            "0-2 years": random.randint(1, 2),
            "2-5 years": random.randint(2, 3),
            "5-10 years": random.randint(3, 4),
            "10-20 years": random.randint(4, 5)
        }
        exp_count = count_map.get(exp_level, 0)
        
        exp = []
        current_year = 2026
        
        for i in range(exp_count):
            start_yr = current_year - random.randint(1, 4)
            end_yr = current_year if i == 0 else start_yr + random.randint(1, 3)
            current_year = start_yr
            
            company = f"{self.fake.company()} {random.choice(pools.COMPANY_SUFFIXES)}"
            title = f"{'Senior ' if i > 1 else ''}{industry} Professional"
            
            resp_count = random.randint(3, 5)
            responsibilities = []
            for _ in range(resp_count):
                verb = random.choice(pools.RESPONSIBILITY_VERBS)
                noun = self.fake.bs()
                metric = f" by {random.randint(10, 50)}%" if random.random() > 0.5 else ""
                responsibilities.append(f"{verb} {noun}{metric}.")
                
            exp.append({
                "company": company,
                "title": title,
                "start_date": f"{self.fake.month_name()} {start_yr}",
                "end_date": "Present" if i == 0 else f"{self.fake.month_name()} {end_yr}",
                "responsibilities": responsibilities
            })
        return exp

    def _generate_projects(self, industry: str) -> List[Dict[str, Any]]:
        proj_count = random.randint(2, 4)
        projects = []
        
        for _ in range(proj_count):
            name = self.fake.catch_phrase().title()
            tech_count = random.randint(2, 4)
            tech = random.sample(pools.TECH_STACK['languages'] + pools.TECH_STACK['frameworks'], tech_count)
            
            desc_len = random.randint(1, 2)
            desc = " ".join([f"{random.choice(pools.PROJECT_VERBS)} {self.fake.bs()}." for _ in range(desc_len)])
            
            projects.append({
                "name": name,
                "technologies": tech,
                "description": desc,
                "link": f"github.com/fake/{name.replace(' ', '').lower()}" if random.random() > 0.5 else None
            })
        return projects
