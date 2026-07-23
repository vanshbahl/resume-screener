
from app.parsers.core.base import BaseParserStage
from app.parsers.core.document import BaseDocument, PipelineContext


class NormalizationStage(BaseParserStage):
    def run(self, document: BaseDocument, context: PipelineContext) -> None:
        # extracted_entities has already been mutated in-place by EntityFusionStage.
        # We perform light normalization before validation.
        entities = document.extracted_entities

        pi = entities.get("personal_info", {})

        # Normalize name: strip extra whitespace, title-case if all-caps
        name_field = pi.get("name")
        if name_field and name_field.get("value"):
            val = name_field["value"].strip()
            if val.isupper():
                val = val.title()
            name_field["value"] = val

        # Normalize phone: collapse multiple spaces/dashes into standard format
        phone_field = pi.get("phone")
        if phone_field and phone_field.get("value"):
            phone_field["value"] = phone_field["value"].strip()

        # Normalize URLs: strip trailing slashes on linkedin/github
        for link_key in ["linkedin", "github", "portfolio", "website"]:
            field = pi.get(link_key)
            if field and field.get("value"):
                field["value"] = field["value"].rstrip("/")

        # Deduplicate flat skills list by value (case-insensitive)
        for cat in [
            "skills",
            "languages",
            "frameworks",
            "tools",
            "concepts",
            "soft_skills",
        ]:
            seen = set()
            deduped = []
            for item in entities.get(cat, []):
                key = item.get("value", "").lower()
                if key and key not in seen:
                    seen.add(key)
                    deduped.append(item)
            entities[cat] = deduped

        document.normalized_entities = entities
