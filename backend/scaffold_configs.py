import os
import yaml

os.makedirs('config/ontology', exist_ok=True)

configs = {
    'config/ontology/languages.yaml': {
        'Python': {'aliases': ['py', 'python3'], 'family': 'Backend'},
        'Java': {'aliases': ['java 8', 'java 11'], 'family': 'Backend'},
        'JavaScript': {'aliases': ['js', 'es6'], 'family': 'Frontend'},
    },
    'config/ontology/frameworks.yaml': {
        'React': {'aliases': ['reactjs', 'react.js'], 'family': 'Frontend', 'prerequisites': ['JavaScript']},
        'FastAPI': {'aliases': ['fast api'], 'family': 'Backend', 'prerequisites': ['Python']},
    },
    'config/ontology/tools.yaml': {
        'Docker': {'aliases': ['dockerize'], 'family': 'DevOps'},
        'Kubernetes': {'aliases': ['k8s'], 'family': 'DevOps'},
    },
    'config/ontology/databases.yaml': {
        'PostgreSQL': {'aliases': ['postgres', 'psql'], 'family': 'Database'},
        'MongoDB': {'aliases': ['mongo'], 'family': 'Database'},
    },
    'config/ontology/cloud.yaml': {
        'AWS': {'aliases': ['amazon web services'], 'family': 'Cloud'},
        'GCP': {'aliases': ['google cloud platform'], 'family': 'Cloud'},
    },
    'config/ontology/concepts.yaml': {
        'REST': {'aliases': ['restful', 'rest api'], 'family': 'Architecture'},
        'Microservices': {'aliases': ['micro-services'], 'family': 'Architecture'},
    },
    'config/matching_weights.yaml': {
        'weights': {
            'technical_skills': 0.30,
            'experience': 0.25,
            'projects': 0.15,
            'education': 0.10,
            'responsibilities': 0.10,
            'soft_skills': 0.05,
            'other': 0.05
        }
    },
    'config/experience_weights.yaml': {
        'tiers': {
            '0-2': 1.0,
            '3-5': 2.0,
            '6-10': 3.0,
            '10+': 4.0
        }
    },
    'config/education_weights.yaml': {
        'tiers': {
            'high_school': 10,
            'bachelors': 40,
            'masters': 70,
            'phd': 100
        }
    },
    'config/ranking.yaml': {
        'ranking_factors': {
            'score_threshold': 50,
            'diversity_bonus': 5
        }
    },
    'config/industry_mapping.yaml': {
        'fintech': ['finance', 'banking', 'trading'],
        'healthtech': ['medical', 'healthcare', 'hospital']
    }
}

for path, data in configs.items():
    with open(path, 'w') as f:
        yaml.dump(data, f, default_flow_style=False)

print("Configuration files scaffolded.")
