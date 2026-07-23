import glob
import os
from typing import Dict, List, Optional

from app.parsers.core.config_loader import load_config


class OntologyService:
    def __init__(self, ontology_dir: str = "config/ontology"):
        self.ontology_dir = ontology_dir
        self.graph: Dict[str, dict] = {}
        self.alias_map: Dict[str, str] = {}
        self._load_ontology()

    def _load_ontology(self):
        """Loads all YAML files in the ontology directory and merges them into a single in-memory graph."""
        if not os.path.exists(self.ontology_dir):
            return

        yaml_files = glob.glob(os.path.join(self.ontology_dir, "*.yaml"))
        for file_path in yaml_files:
            # Reusing the existing load_config which caches the read
            file_name = os.path.basename(file_path)
            data = load_config(f"ontology/{file_name}")

            if not isinstance(data, dict):
                continue

            for canonical_name, props in data.items():
                self.graph[canonical_name] = props

                # Build reverse lookup for aliases
                self.alias_map[canonical_name.lower()] = canonical_name
                aliases = props.get("aliases", [])
                for alias in aliases:
                    self.alias_map[alias.lower()] = canonical_name

    def get_canonical_name(self, skill_name: str) -> str:
        """Resolves an alias to its canonical name. Returns the original name capitalized if not found."""
        if not skill_name:
            return ""
        return self.alias_map.get(skill_name.lower(), skill_name.strip().title())

    def get_semantic_family(self, canonical_name: str) -> Optional[str]:
        node = self.graph.get(canonical_name)
        if node:
            return node.get("family")
        return None

    def get_prerequisites(self, canonical_name: str) -> List[str]:
        node = self.graph.get(canonical_name)
        if node:
            return node.get("prerequisites", [])
        return []

    def get_related(self, canonical_name: str) -> List[str]:
        """Gets siblings in the same family."""
        family = self.get_semantic_family(canonical_name)
        if not family:
            return []

        related = []
        for name, props in self.graph.items():
            if name != canonical_name and props.get("family") == family:
                related.append(name)
        return related


# Singleton instance
ontology_service = OntologyService()
