from typing import Any, Dict


def generate_markdown(profile: Dict[str, Any]) -> str:
    """Generates a Markdown string from a ResumeProfile."""
    md = []

    pi = profile.get("personal_info", {})
    md.append(f"# {pi.get('name', 'Unknown')}")

    # Contact Info
    contact = []
    if pi.get("email"):
        contact.append(pi["email"])
    if pi.get("phone"):
        contact.append(pi["phone"])
    if pi.get("location"):
        contact.append(pi["location"])
    if pi.get("github"):
        contact.append(pi["github"])
    if pi.get("linkedin"):
        contact.append(pi["linkedin"])
    if pi.get("portfolio"):
        contact.append(pi["portfolio"])

    md.append(" | ".join(contact))
    md.append("\n---")

    # Summary
    if profile.get("summary"):
        md.append("## Summary")
        md.append(profile["summary"])
        md.append("\n---")

    # We will randomly order sections to increase dataset diversity
    # But for markdown simplicity, let's keep a standard order
    # The actual PDF renderer might vary the order.

    if profile.get("experience"):
        md.append("## Experience")
        for exp in profile["experience"]:
            md.append(f"### {exp['title']}")
            md.append(f"**{exp['company']}** | {exp['start_date']} - {exp['end_date']}")
            for resp in exp.get("responsibilities", []):
                md.append(f"- {resp}")
            md.append("")
        md.append("---")

    if profile.get("projects"):
        md.append("## Projects")
        for proj in profile["projects"]:
            link = f" ({proj['link']})" if proj.get("link") else ""
            md.append(f"### {proj['name']}{link}")
            if proj.get("technologies"):
                md.append(f"**Technologies:** {', '.join(proj['technologies'])}")
            md.append(f"- {proj['description']}")
            md.append("")
        md.append("---")

    if profile.get("education"):
        md.append("## Education")
        for edu in profile["education"]:
            cgpa = f" | CGPA: {edu['cgpa']}" if edu.get("cgpa") else ""
            md.append(f"**{edu['institution']}**")
            md.append(f"{edu['degree']} | {edu['graduation_year']}{cgpa}")
            md.append("")
        md.append("---")

    if profile.get("skills"):
        md.append("## Skills")
        s = profile["skills"]
        if s.get("languages"):
            md.append(f"**Languages:** {', '.join(s['languages'])}")
        if s.get("frameworks"):
            md.append(f"**Frameworks:** {', '.join(s['frameworks'])}")
        if s.get("tools"):
            md.append(f"**Tools:** {', '.join(s['tools'])}")

    return "\n".join(md)
