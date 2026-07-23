from typing import Any, Dict

from fpdf import FPDF


class ResumePDF(FPDF):
    def __init__(self):
        super().__init__()
        # Use built-in fonts (Helvetica, Times, Courier) since fpdf2 does not require custom TTFs for basic use.
        self.set_auto_page_break(auto=True, margin=15)
        self.add_page()

    def add_section_title(self, title: str):
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(0, 0, 0)
        self.cell(0, 10, title.upper(), border=0, ln=True, align="L")
        self.line(self.get_x(), self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(3)


def generate_pdf(profile: Dict[str, Any], output_path: str):
    pdf = ResumePDF()
    pi = profile.get("personal_info", {})

    # Header / Name
    pdf.set_font("Helvetica", "B", 24)
    pdf.cell(0, 10, pi.get("name", "Unknown"), ln=True, align="C")

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

    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, " | ".join(contact), ln=True, align="C")
    pdf.ln(5)

    # Summary
    if profile.get("summary"):
        pdf.add_section_title("Summary")
        pdf.set_font("Helvetica", "", 11)
        pdf.multi_cell(190, 6, profile["summary"])
        pdf.ln(4)

    # Experience
    if profile.get("experience"):
        pdf.add_section_title("Experience")
        for exp in profile["experience"]:
            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(0, 6, exp["title"], ln=True)

            pdf.set_font("Helvetica", "I", 11)
            pdf.cell(
                0,
                6,
                f"{exp['company']} | {exp['start_date']} - {exp['end_date']}",
                ln=True,
            )

            pdf.set_font("Helvetica", "", 11)
            for resp in exp.get("responsibilities", []):
                # Simple bullet point
                pdf.multi_cell(190, 6, f"- {resp}")
            pdf.ln(3)

    # Projects
    if profile.get("projects"):
        pdf.add_section_title("Projects")
        for proj in profile["projects"]:
            pdf.set_font("Helvetica", "B", 12)
            link = f" ({proj['link']})" if proj.get("link") else ""
            pdf.cell(0, 6, f"{proj['name']}{link}", ln=True)

            if proj.get("technologies"):
                pdf.set_font("Helvetica", "I", 10)
                pdf.cell(
                    0, 5, f"Technologies: {', '.join(proj['technologies'])}", ln=True
                )

            pdf.set_font("Helvetica", "", 11)
            pdf.multi_cell(190, 6, f"- {proj['description']}")
            pdf.ln(3)

    # Education
    if profile.get("education"):
        pdf.add_section_title("Education")
        for edu in profile["education"]:
            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(0, 6, edu["institution"], ln=True)

            cgpa = f" | CGPA: {edu['cgpa']}" if edu.get("cgpa") else ""
            pdf.set_font("Helvetica", "", 11)
            pdf.cell(0, 6, f"{edu['degree']} | {edu['graduation_year']}{cgpa}", ln=True)
            pdf.ln(2)

    # Skills
    if profile.get("skills"):
        pdf.add_section_title("Skills")
        pdf.set_font("Helvetica", "", 11)
        s = profile["skills"]
        if s.get("languages"):
            pdf.multi_cell(190, 6, f"Languages: {', '.join(s['languages'])}")
        if s.get("frameworks"):
            pdf.multi_cell(190, 6, f"Frameworks: {', '.join(s['frameworks'])}")
        if s.get("tools"):
            pdf.multi_cell(190, 6, f"Tools: {', '.join(s['tools'])}")

    pdf.output(output_path)
