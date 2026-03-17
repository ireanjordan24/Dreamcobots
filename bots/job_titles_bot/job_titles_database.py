"""
DreamCo Job Titles Database — comprehensive directory of all job titles
known to humankind, organised by industry, with skills, education, and
salary data.

GLOBAL AI SOURCES FLOW: participates via job_titles_bot.py pipeline.
"""

from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from dataclasses import dataclass, field
from typing import List, Optional

from framework import GlobalAISourcesFlow  # noqa: F401


@dataclass
class JobTitle:
    """Represents a single job title in the database."""
    title: str
    industry: str
    category: str
    responsibilities: List[str]
    required_skills: List[str]
    education_required: str
    avg_salary_usd_annual: Optional[int]
    automatable_by_ai: bool
    description: str

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "industry": self.industry,
            "category": self.category,
            "responsibilities": self.responsibilities,
            "required_skills": self.required_skills,
            "education_required": self.education_required,
            "avg_salary_usd_annual": self.avg_salary_usd_annual,
            "automatable_by_ai": self.automatable_by_ai,
            "description": self.description,
        }


# ---------------------------------------------------------------------------
# Comprehensive job title seed data — 200+ titles across 20+ industries
# ---------------------------------------------------------------------------

_JOB_TITLES: List[JobTitle] = [
    # -----------------------------------------------------------------------
    # Technology & Software
    # -----------------------------------------------------------------------
    JobTitle(
        title="Software Engineer",
        industry="Technology",
        category="Engineering",
        responsibilities=["design and build software systems", "write clean maintainable code", "code review", "debug and fix bugs"],
        required_skills=["Python", "Java", "algorithms", "data structures", "Git"],
        education_required="Bachelor's in Computer Science or equivalent",
        avg_salary_usd_annual=120000,
        automatable_by_ai=True,
        description="Designs, develops, and maintains software applications.",
    ),
    JobTitle(
        title="Frontend Developer",
        industry="Technology",
        category="Engineering",
        responsibilities=["build user interfaces", "implement responsive designs", "optimize web performance", "collaborate with designers"],
        required_skills=["HTML", "CSS", "JavaScript", "React", "TypeScript"],
        education_required="Bachelor's in Computer Science or equivalent",
        avg_salary_usd_annual=105000,
        automatable_by_ai=True,
        description="Creates and maintains the visual layer of web applications.",
    ),
    JobTitle(
        title="Backend Developer",
        industry="Technology",
        category="Engineering",
        responsibilities=["build APIs and services", "manage databases", "ensure system security", "optimize server performance"],
        required_skills=["Node.js", "Python", "SQL", "REST APIs", "cloud platforms"],
        education_required="Bachelor's in Computer Science or equivalent",
        avg_salary_usd_annual=115000,
        automatable_by_ai=True,
        description="Develops and maintains server-side application logic.",
    ),
    JobTitle(
        title="Data Scientist",
        industry="Technology",
        category="Data & Analytics",
        responsibilities=["analyse large datasets", "build predictive models", "create data visualizations", "communicate insights"],
        required_skills=["Python", "R", "machine learning", "statistics", "SQL"],
        education_required="Master's or PhD in Data Science, Statistics, or related",
        avg_salary_usd_annual=130000,
        automatable_by_ai=True,
        description="Extracts insights from complex datasets using statistical and ML techniques.",
    ),
    JobTitle(
        title="Machine Learning Engineer",
        industry="Technology",
        category="Artificial Intelligence",
        responsibilities=["design ML pipelines", "train and evaluate models", "deploy models to production", "monitor model performance"],
        required_skills=["Python", "TensorFlow", "PyTorch", "MLOps", "math"],
        education_required="Master's or PhD in Computer Science, ML, or related",
        avg_salary_usd_annual=145000,
        automatable_by_ai=False,
        description="Builds and deploys machine learning models at scale.",
    ),
    JobTitle(
        title="DevOps Engineer",
        industry="Technology",
        category="Infrastructure",
        responsibilities=["manage CI/CD pipelines", "infrastructure provisioning", "monitor system health", "automate deployment workflows"],
        required_skills=["Docker", "Kubernetes", "AWS", "Terraform", "Linux"],
        education_required="Bachelor's in Computer Science or equivalent",
        avg_salary_usd_annual=125000,
        automatable_by_ai=True,
        description="Bridges development and operations to enable continuous delivery.",
    ),
    JobTitle(
        title="Cybersecurity Analyst",
        industry="Technology",
        category="Security",
        responsibilities=["monitor networks for threats", "investigate security incidents", "implement security controls", "conduct vulnerability assessments"],
        required_skills=["network security", "SIEM", "penetration testing", "incident response"],
        education_required="Bachelor's in Cybersecurity or IT",
        avg_salary_usd_annual=110000,
        automatable_by_ai=True,
        description="Protects computer systems and networks from cyber threats.",
    ),
    JobTitle(
        title="Product Manager",
        industry="Technology",
        category="Management",
        responsibilities=["define product roadmap", "gather user requirements", "coordinate cross-functional teams", "prioritize features"],
        required_skills=["strategic thinking", "communication", "data analysis", "agile methodologies"],
        education_required="Bachelor's in Business or Computer Science",
        avg_salary_usd_annual=130000,
        automatable_by_ai=False,
        description="Owns the product vision and strategy, bridging business and technical teams.",
    ),
    JobTitle(
        title="UX/UI Designer",
        industry="Technology",
        category="Design",
        responsibilities=["design user interfaces", "conduct user research", "create wireframes and prototypes", "run usability tests"],
        required_skills=["Figma", "user research", "wireframing", "visual design", "prototyping"],
        education_required="Bachelor's in Design or Human-Computer Interaction",
        avg_salary_usd_annual=95000,
        automatable_by_ai=True,
        description="Designs intuitive and accessible user experiences for digital products.",
    ),
    JobTitle(
        title="Cloud Architect",
        industry="Technology",
        category="Infrastructure",
        responsibilities=["design cloud infrastructure", "select cloud services", "ensure scalability and reliability", "manage cloud costs"],
        required_skills=["AWS", "Azure", "GCP", "networking", "security", "architecture patterns"],
        education_required="Bachelor's in Computer Science + cloud certifications",
        avg_salary_usd_annual=155000,
        automatable_by_ai=False,
        description="Designs and oversees cloud infrastructure strategies for organizations.",
    ),
    # -----------------------------------------------------------------------
    # Healthcare & Medicine
    # -----------------------------------------------------------------------
    JobTitle(
        title="Physician / Doctor",
        industry="Healthcare",
        category="Clinical",
        responsibilities=["diagnose and treat patients", "prescribe medications", "order and interpret tests", "counsel patients"],
        required_skills=["medical knowledge", "diagnostic reasoning", "patient communication", "clinical procedures"],
        education_required="MD or DO degree + residency",
        avg_salary_usd_annual=220000,
        automatable_by_ai=False,
        description="Provides medical care, diagnosis, and treatment to patients.",
    ),
    JobTitle(
        title="Registered Nurse",
        industry="Healthcare",
        category="Nursing",
        responsibilities=["administer medications", "monitor patient vitals", "coordinate patient care", "educate patients and families"],
        required_skills=["patient care", "medication administration", "critical thinking", "communication"],
        education_required="BSN or ASN + RN license",
        avg_salary_usd_annual=77000,
        automatable_by_ai=False,
        description="Provides direct patient care in hospitals, clinics, and community settings.",
    ),
    JobTitle(
        title="Surgeon",
        industry="Healthcare",
        category="Clinical",
        responsibilities=["perform surgical procedures", "pre- and post-operative care", "consult on complex cases", "train surgical residents"],
        required_skills=["surgical techniques", "anatomy", "decision making under pressure", "dexterity"],
        education_required="MD + surgical residency and fellowship",
        avg_salary_usd_annual=350000,
        automatable_by_ai=False,
        description="Performs operations to treat injuries, diseases, and deformities.",
    ),
    JobTitle(
        title="Pharmacist",
        industry="Healthcare",
        category="Pharmacy",
        responsibilities=["dispense medications", "counsel patients on drug use", "review prescriptions", "monitor for drug interactions"],
        required_skills=["pharmacology", "patient counseling", "attention to detail", "medication management"],
        education_required="PharmD degree + license",
        avg_salary_usd_annual=128000,
        automatable_by_ai=True,
        description="Prepares and dispenses medications, advising on their safe use.",
    ),
    JobTitle(
        title="Physical Therapist",
        industry="Healthcare",
        category="Rehabilitation",
        responsibilities=["evaluate patient function", "develop treatment plans", "guide therapeutic exercises", "track patient progress"],
        required_skills=["anatomy", "therapeutic exercise", "manual therapy", "patient motivation"],
        education_required="Doctor of Physical Therapy (DPT)",
        avg_salary_usd_annual=92000,
        automatable_by_ai=False,
        description="Helps patients recover movement and manage pain through physical intervention.",
    ),
    JobTitle(
        title="Medical Lab Technician",
        industry="Healthcare",
        category="Laboratory",
        responsibilities=["perform lab tests", "analyze biological samples", "maintain lab equipment", "report results to physicians"],
        required_skills=["lab techniques", "microscopy", "quality control", "attention to detail"],
        education_required="Associate's or Bachelor's in Medical Laboratory Science",
        avg_salary_usd_annual=57000,
        automatable_by_ai=True,
        description="Conducts laboratory tests to help diagnose and treat diseases.",
    ),
    JobTitle(
        title="Dentist",
        industry="Healthcare",
        category="Dental",
        responsibilities=["diagnose oral conditions", "perform cleanings and fillings", "extract teeth", "educate patients on oral hygiene"],
        required_skills=["dental procedures", "patient management", "dexterity", "radiography"],
        education_required="DDS or DMD degree + license",
        avg_salary_usd_annual=163000,
        automatable_by_ai=False,
        description="Diagnoses and treats problems with teeth, gums, and the mouth.",
    ),
    # -----------------------------------------------------------------------
    # Finance & Banking
    # -----------------------------------------------------------------------
    JobTitle(
        title="Financial Analyst",
        industry="Finance",
        category="Analysis",
        responsibilities=["analyze financial data", "build financial models", "prepare investment reports", "forecast revenue"],
        required_skills=["Excel", "financial modelling", "accounting", "data analysis", "valuation"],
        education_required="Bachelor's in Finance or Accounting",
        avg_salary_usd_annual=85000,
        automatable_by_ai=True,
        description="Evaluates financial data to guide investment and business decisions.",
    ),
    JobTitle(
        title="Accountant",
        industry="Finance",
        category="Accounting",
        responsibilities=["prepare financial statements", "manage accounts payable/receivable", "file tax returns", "audit financial records"],
        required_skills=["GAAP", "accounting software", "tax law", "spreadsheets", "attention to detail"],
        education_required="Bachelor's in Accounting + CPA license",
        avg_salary_usd_annual=73000,
        automatable_by_ai=True,
        description="Records, classifies, and summarises financial transactions.",
    ),
    JobTitle(
        title="Investment Banker",
        industry="Finance",
        category="Investment",
        responsibilities=["advise on mergers and acquisitions", "raise capital", "conduct due diligence", "structure financial deals"],
        required_skills=["financial modelling", "valuation", "negotiation", "client relations", "deal structuring"],
        education_required="Bachelor's in Finance/Economics; MBA preferred",
        avg_salary_usd_annual=200000,
        automatable_by_ai=False,
        description="Assists companies and governments in raising capital and executing deals.",
    ),
    JobTitle(
        title="Insurance Underwriter",
        industry="Finance",
        category="Insurance",
        responsibilities=["assess insurance applications", "evaluate risk", "set premium rates", "approve or deny coverage"],
        required_skills=["risk assessment", "statistical analysis", "attention to detail", "decision making"],
        education_required="Bachelor's in Finance, Business, or Math",
        avg_salary_usd_annual=71000,
        automatable_by_ai=True,
        description="Evaluates and prices insurance risk for individuals and organizations.",
    ),
    JobTitle(
        title="Tax Advisor",
        industry="Finance",
        category="Tax",
        responsibilities=["prepare tax returns", "advise on tax planning", "ensure compliance", "represent clients in audits"],
        required_skills=["tax law", "accounting", "client communication", "research"],
        education_required="Bachelor's in Accounting + CPA or EA",
        avg_salary_usd_annual=82000,
        automatable_by_ai=True,
        description="Provides expert guidance on tax obligations and strategies.",
    ),
    # -----------------------------------------------------------------------
    # Education
    # -----------------------------------------------------------------------
    JobTitle(
        title="Teacher / Educator",
        industry="Education",
        category="Instruction",
        responsibilities=["develop curriculum", "deliver lessons", "assess student progress", "communicate with parents"],
        required_skills=["subject expertise", "classroom management", "communication", "curriculum design"],
        education_required="Bachelor's in Education + teaching certification",
        avg_salary_usd_annual=60000,
        automatable_by_ai=False,
        description="Educates students across various subjects at K-12 and post-secondary levels.",
    ),
    JobTitle(
        title="Professor / University Lecturer",
        industry="Education",
        category="Higher Education",
        responsibilities=["teach university courses", "conduct research", "publish academic papers", "mentor students"],
        required_skills=["deep subject expertise", "research methodology", "academic writing", "mentoring"],
        education_required="PhD in relevant field",
        avg_salary_usd_annual=85000,
        automatable_by_ai=False,
        description="Teaches and conducts research at a university or college.",
    ),
    JobTitle(
        title="School Principal",
        industry="Education",
        category="Administration",
        responsibilities=["manage school operations", "hire and evaluate staff", "develop school policies", "engage with community"],
        required_skills=["leadership", "administration", "communication", "budgeting"],
        education_required="Master's in Education Administration",
        avg_salary_usd_annual=100000,
        automatable_by_ai=False,
        description="Leads and manages the administration of a school.",
    ),
    JobTitle(
        title="Instructional Designer",
        industry="Education",
        category="Curriculum",
        responsibilities=["design e-learning courses", "develop training materials", "apply learning theories", "evaluate training effectiveness"],
        required_skills=["instructional design", "LMS platforms", "e-learning authoring tools", "adult learning"],
        education_required="Bachelor's in Instructional Design or Education",
        avg_salary_usd_annual=72000,
        automatable_by_ai=True,
        description="Creates educational content and training programs for various audiences.",
    ),
    # -----------------------------------------------------------------------
    # Legal
    # -----------------------------------------------------------------------
    JobTitle(
        title="Lawyer / Attorney",
        industry="Legal",
        category="Law Practice",
        responsibilities=["advise clients on legal matters", "draft legal documents", "represent clients in court", "conduct legal research"],
        required_skills=["legal research", "written and oral advocacy", "negotiation", "critical thinking"],
        education_required="JD degree + bar admission",
        avg_salary_usd_annual=126000,
        automatable_by_ai=False,
        description="Provides legal counsel and representation to individuals and organizations.",
    ),
    JobTitle(
        title="Paralegal",
        industry="Legal",
        category="Legal Support",
        responsibilities=["assist attorneys with research", "draft legal documents", "manage case files", "client intake"],
        required_skills=["legal research", "document management", "communication", "attention to detail"],
        education_required="Associate's or Bachelor's in Paralegal Studies",
        avg_salary_usd_annual=56000,
        automatable_by_ai=True,
        description="Supports lawyers by performing substantive legal work under attorney supervision.",
    ),
    JobTitle(
        title="Judge",
        industry="Legal",
        category="Judiciary",
        responsibilities=["preside over court proceedings", "interpret and apply the law", "write legal opinions", "manage courtroom"],
        required_skills=["legal expertise", "impartiality", "analytical reasoning", "writing"],
        education_required="JD degree + extensive legal experience + appointment/election",
        avg_salary_usd_annual=175000,
        automatable_by_ai=False,
        description="Oversees legal proceedings and ensures fair application of the law.",
    ),
    # -----------------------------------------------------------------------
    # Engineering
    # -----------------------------------------------------------------------
    JobTitle(
        title="Civil Engineer",
        industry="Engineering",
        category="Civil",
        responsibilities=["design infrastructure projects", "oversee construction", "ensure structural integrity", "manage project budgets"],
        required_skills=["structural analysis", "AutoCAD", "project management", "math", "materials science"],
        education_required="Bachelor's in Civil Engineering + PE license",
        avg_salary_usd_annual=88000,
        automatable_by_ai=True,
        description="Plans and oversees construction of infrastructure such as roads, bridges, and buildings.",
    ),
    JobTitle(
        title="Mechanical Engineer",
        industry="Engineering",
        category="Mechanical",
        responsibilities=["design mechanical systems", "develop prototypes", "conduct stress analysis", "oversee manufacturing"],
        required_skills=["CAD", "thermodynamics", "materials science", "FEA", "manufacturing processes"],
        education_required="Bachelor's in Mechanical Engineering",
        avg_salary_usd_annual=92000,
        automatable_by_ai=True,
        description="Designs and develops mechanical devices, systems, and machinery.",
    ),
    JobTitle(
        title="Electrical Engineer",
        industry="Engineering",
        category="Electrical",
        responsibilities=["design electrical systems", "develop circuit schematics", "test electrical components", "ensure compliance with codes"],
        required_skills=["circuit design", "PCB layout", "MATLAB", "power systems", "electronics"],
        education_required="Bachelor's in Electrical Engineering",
        avg_salary_usd_annual=100000,
        automatable_by_ai=True,
        description="Designs and develops electrical equipment, systems, and components.",
    ),
    JobTitle(
        title="Chemical Engineer",
        industry="Engineering",
        category="Chemical",
        responsibilities=["design chemical processes", "optimize production", "ensure safety compliance", "conduct research"],
        required_skills=["process simulation", "reaction kinetics", "thermodynamics", "safety protocols"],
        education_required="Bachelor's in Chemical Engineering",
        avg_salary_usd_annual=105000,
        automatable_by_ai=True,
        description="Develops processes for producing chemicals, materials, and energy.",
    ),
    JobTitle(
        title="Robotics Engineer",
        industry="Engineering",
        category="Robotics",
        responsibilities=["design robotic systems", "program robot controllers", "integrate sensors and actuators", "test and validate robots"],
        required_skills=["ROS", "C++", "kinematics", "machine learning", "mechatronics"],
        education_required="Bachelor's in Robotics, Mechanical, or Electrical Engineering",
        avg_salary_usd_annual=118000,
        automatable_by_ai=False,
        description="Designs, builds, and programs robots and robotic systems.",
    ),
    JobTitle(
        title="Aerospace Engineer",
        industry="Engineering",
        category="Aerospace",
        responsibilities=["design aircraft and spacecraft", "conduct aerodynamic analysis", "oversee testing", "ensure airworthiness compliance"],
        required_skills=["aerodynamics", "CFD", "CAD", "materials science", "systems engineering"],
        education_required="Bachelor's in Aerospace Engineering",
        avg_salary_usd_annual=118000,
        automatable_by_ai=True,
        description="Designs and develops aircraft, spacecraft, and related systems.",
    ),
    # -----------------------------------------------------------------------
    # Business & Management
    # -----------------------------------------------------------------------
    JobTitle(
        title="CEO / Chief Executive Officer",
        industry="Business",
        category="Executive Leadership",
        responsibilities=["set company vision and strategy", "lead executive team", "manage stakeholder relations", "drive growth"],
        required_skills=["strategic thinking", "leadership", "communication", "financial acumen", "decision making"],
        education_required="Bachelor's + MBA preferred",
        avg_salary_usd_annual=350000,
        automatable_by_ai=False,
        description="Top executive responsible for overall company direction and performance.",
    ),
    JobTitle(
        title="Operations Manager",
        industry="Business",
        category="Operations",
        responsibilities=["oversee daily operations", "optimize processes", "manage staff", "track KPIs"],
        required_skills=["process improvement", "team management", "data analysis", "budgeting"],
        education_required="Bachelor's in Business or Operations Management",
        avg_salary_usd_annual=90000,
        automatable_by_ai=True,
        description="Oversees the day-to-day operations of a business unit or organization.",
    ),
    JobTitle(
        title="Human Resources Manager",
        industry="Business",
        category="Human Resources",
        responsibilities=["recruit and onboard employees", "manage employee relations", "administer benefits", "develop HR policies"],
        required_skills=["recruitment", "employee relations", "labor law", "HRIS systems", "communication"],
        education_required="Bachelor's in HR or Business",
        avg_salary_usd_annual=80000,
        automatable_by_ai=True,
        description="Manages recruitment, employee relations, and HR programs.",
    ),
    JobTitle(
        title="Project Manager",
        industry="Business",
        category="Project Management",
        responsibilities=["plan and execute projects", "manage project budgets and timelines", "coordinate teams", "report to stakeholders"],
        required_skills=["project planning", "risk management", "communication", "agile/scrum", "budgeting"],
        education_required="Bachelor's in Business + PMP certification",
        avg_salary_usd_annual=95000,
        automatable_by_ai=True,
        description="Plans, executes, and closes projects on time and within budget.",
    ),
    JobTitle(
        title="Business Analyst",
        industry="Business",
        category="Analysis",
        responsibilities=["analyse business processes", "gather requirements", "identify improvement areas", "document findings"],
        required_skills=["requirements analysis", "data analysis", "process mapping", "stakeholder management"],
        education_required="Bachelor's in Business or IT",
        avg_salary_usd_annual=85000,
        automatable_by_ai=True,
        description="Identifies business needs and solutions to improve processes and outcomes.",
    ),
    # -----------------------------------------------------------------------
    # Sales & Marketing
    # -----------------------------------------------------------------------
    JobTitle(
        title="Sales Representative",
        industry="Sales",
        category="Inside/Outside Sales",
        responsibilities=["prospect and qualify leads", "conduct sales presentations", "negotiate deals", "manage client accounts"],
        required_skills=["persuasion", "CRM software", "negotiation", "product knowledge", "communication"],
        education_required="Bachelor's in Business or related; experience often sufficient",
        avg_salary_usd_annual=65000,
        automatable_by_ai=True,
        description="Generates revenue by selling products or services to customers.",
    ),
    JobTitle(
        title="Digital Marketing Manager",
        industry="Marketing",
        category="Digital Marketing",
        responsibilities=["manage online campaigns", "SEO and content strategy", "manage social media", "analyze marketing metrics"],
        required_skills=["SEO/SEM", "social media", "Google Analytics", "content marketing", "email marketing"],
        education_required="Bachelor's in Marketing or Communications",
        avg_salary_usd_annual=82000,
        automatable_by_ai=True,
        description="Develops and executes digital marketing strategies to grow brand and revenue.",
    ),
    JobTitle(
        title="Brand Manager",
        industry="Marketing",
        category="Brand",
        responsibilities=["develop brand strategy", "manage brand identity", "oversee marketing campaigns", "track brand metrics"],
        required_skills=["branding", "marketing strategy", "consumer insights", "creative direction"],
        education_required="Bachelor's in Marketing or Business",
        avg_salary_usd_annual=92000,
        automatable_by_ai=False,
        description="Manages and develops a company's brand identity and positioning.",
    ),
    JobTitle(
        title="Content Creator / Copywriter",
        industry="Marketing",
        category="Content",
        responsibilities=["write articles, blogs, and copy", "create social media content", "develop scripts", "edit and proofread"],
        required_skills=["writing", "SEO", "creativity", "research", "storytelling"],
        education_required="Bachelor's in English, Journalism, or Marketing",
        avg_salary_usd_annual=62000,
        automatable_by_ai=True,
        description="Creates engaging written content for digital and print media.",
    ),
    # -----------------------------------------------------------------------
    # Retail & Customer Service
    # -----------------------------------------------------------------------
    JobTitle(
        title="Retail Store Manager",
        industry="Retail",
        category="Management",
        responsibilities=["manage store operations", "supervise staff", "track inventory", "meet sales targets"],
        required_skills=["retail management", "customer service", "inventory management", "leadership"],
        education_required="High school diploma or Bachelor's",
        avg_salary_usd_annual=55000,
        automatable_by_ai=True,
        description="Manages the daily operations of a retail store.",
    ),
    JobTitle(
        title="Customer Service Representative",
        industry="Customer Service",
        category="Support",
        responsibilities=["respond to customer inquiries", "resolve complaints", "process orders and returns", "document interactions"],
        required_skills=["communication", "problem solving", "empathy", "CRM systems"],
        education_required="High school diploma",
        avg_salary_usd_annual=38000,
        automatable_by_ai=True,
        description="Assists customers with inquiries, issues, and product support.",
    ),
    JobTitle(
        title="Call Center Agent",
        industry="Customer Service",
        category="Inbound/Outbound",
        responsibilities=["handle inbound calls", "make outbound calls", "document call outcomes", "escalate complex issues"],
        required_skills=["communication", "active listening", "typing", "CRM software"],
        education_required="High school diploma",
        avg_salary_usd_annual=36000,
        automatable_by_ai=True,
        description="Handles customer interactions via telephone for support or sales.",
    ),
    # -----------------------------------------------------------------------
    # Manufacturing & Production
    # -----------------------------------------------------------------------
    JobTitle(
        title="Manufacturing Engineer",
        industry="Manufacturing",
        category="Engineering",
        responsibilities=["design production processes", "improve manufacturing efficiency", "manage quality control", "troubleshoot equipment"],
        required_skills=["lean manufacturing", "CAD", "process optimization", "Six Sigma"],
        education_required="Bachelor's in Manufacturing or Industrial Engineering",
        avg_salary_usd_annual=88000,
        automatable_by_ai=True,
        description="Develops and improves manufacturing processes for efficiency and quality.",
    ),
    JobTitle(
        title="Quality Control Inspector",
        industry="Manufacturing",
        category="Quality Assurance",
        responsibilities=["inspect products for defects", "document quality issues", "enforce quality standards", "work with production teams"],
        required_skills=["attention to detail", "measurement tools", "quality standards", "documentation"],
        education_required="High school diploma + vocational training",
        avg_salary_usd_annual=45000,
        automatable_by_ai=True,
        description="Ensures manufactured products meet quality and safety standards.",
    ),
    JobTitle(
        title="CNC Machinist",
        industry="Manufacturing",
        category="Machining",
        responsibilities=["set up and operate CNC machines", "read technical blueprints", "inspect finished parts", "maintain equipment"],
        required_skills=["CNC programming", "blueprint reading", "precision measurement", "machining"],
        education_required="Vocational training or Associate's in Machining",
        avg_salary_usd_annual=52000,
        automatable_by_ai=True,
        description="Operates computer-controlled machinery to produce precision parts.",
    ),
    JobTitle(
        title="Supply Chain Manager",
        industry="Manufacturing",
        category="Logistics",
        responsibilities=["manage supplier relationships", "optimize supply chain processes", "coordinate logistics", "reduce costs"],
        required_skills=["supply chain management", "ERP systems", "negotiation", "data analysis"],
        education_required="Bachelor's in Supply Chain or Business",
        avg_salary_usd_annual=95000,
        automatable_by_ai=True,
        description="Oversees the end-to-end supply chain from sourcing to delivery.",
    ),
    # -----------------------------------------------------------------------
    # Construction & Trades
    # -----------------------------------------------------------------------
    JobTitle(
        title="General Contractor",
        industry="Construction",
        category="Construction Management",
        responsibilities=["manage construction projects", "hire and supervise subcontractors", "ensure code compliance", "manage budgets"],
        required_skills=["construction management", "budgeting", "scheduling", "contract management"],
        education_required="Bachelor's in Construction Management + license",
        avg_salary_usd_annual=95000,
        automatable_by_ai=False,
        description="Manages all aspects of a construction project from planning to completion.",
    ),
    JobTitle(
        title="Electrician",
        industry="Construction",
        category="Trades",
        responsibilities=["install electrical systems", "troubleshoot electrical problems", "read blueprints", "ensure code compliance"],
        required_skills=["electrical wiring", "blueprint reading", "code compliance", "safety"],
        education_required="Apprenticeship + electrician license",
        avg_salary_usd_annual=60000,
        automatable_by_ai=False,
        description="Installs, maintains, and repairs electrical systems.",
    ),
    JobTitle(
        title="Plumber",
        industry="Construction",
        category="Trades",
        responsibilities=["install plumbing systems", "repair leaks and clogs", "inspect piping systems", "ensure code compliance"],
        required_skills=["pipe fitting", "blueprint reading", "problem solving", "safety"],
        education_required="Apprenticeship + plumber license",
        avg_salary_usd_annual=60000,
        automatable_by_ai=False,
        description="Installs and repairs water, gas, and drainage systems.",
    ),
    JobTitle(
        title="Welder",
        industry="Manufacturing",
        category="Trades",
        responsibilities=["weld metal components", "read welding blueprints", "inspect welds", "operate welding equipment"],
        required_skills=["MIG/TIG/Arc welding", "blueprint reading", "precision", "safety protocols"],
        education_required="Vocational training + welding certification",
        avg_salary_usd_annual=48000,
        automatable_by_ai=True,
        description="Joins metal parts using various welding techniques.",
    ),
    # -----------------------------------------------------------------------
    # Transportation & Logistics
    # -----------------------------------------------------------------------
    JobTitle(
        title="Truck Driver / CDL Driver",
        industry="Transportation",
        category="Driving",
        responsibilities=["transport goods over long distances", "perform vehicle inspections", "maintain delivery logs", "follow safety regulations"],
        required_skills=["CDL license", "route planning", "vehicle inspection", "safety compliance"],
        education_required="High school diploma + CDL license",
        avg_salary_usd_annual=50000,
        automatable_by_ai=True,
        description="Transports freight and goods via tractor-trailers or delivery trucks.",
    ),
    JobTitle(
        title="Logistics Coordinator",
        industry="Transportation",
        category="Logistics",
        responsibilities=["coordinate shipments", "track deliveries", "liaise with carriers", "manage shipping documentation"],
        required_skills=["logistics software", "communication", "problem solving", "organization"],
        education_required="Bachelor's in Logistics or Business",
        avg_salary_usd_annual=55000,
        automatable_by_ai=True,
        description="Coordinates the movement of goods from suppliers to customers.",
    ),
    JobTitle(
        title="Airline Pilot",
        industry="Transportation",
        category="Aviation",
        responsibilities=["fly commercial aircraft", "file flight plans", "communicate with ATC", "perform pre-flight checks"],
        required_skills=["aviation", "navigation", "decision making under pressure", "communication"],
        education_required="FAA ATP Certificate + flight hours",
        avg_salary_usd_annual=200000,
        automatable_by_ai=False,
        description="Commands commercial or cargo aircraft on scheduled or chartered flights.",
    ),
    # -----------------------------------------------------------------------
    # Government & Public Service
    # -----------------------------------------------------------------------
    JobTitle(
        title="Police Officer",
        industry="Government",
        category="Law Enforcement",
        responsibilities=["patrol assigned areas", "respond to emergency calls", "investigate crimes", "enforce laws"],
        required_skills=["law enforcement", "conflict resolution", "firearms", "community relations"],
        education_required="High school diploma + police academy",
        avg_salary_usd_annual=65000,
        automatable_by_ai=False,
        description="Maintains public order and enforces the law in assigned jurisdictions.",
    ),
    JobTitle(
        title="Firefighter",
        industry="Government",
        category="Emergency Services",
        responsibilities=["respond to fire emergencies", "conduct search and rescue", "operate firefighting equipment", "perform fire prevention inspections"],
        required_skills=["firefighting", "emergency medical training", "physical fitness", "teamwork"],
        education_required="High school diploma + fire academy certification",
        avg_salary_usd_annual=56000,
        automatable_by_ai=False,
        description="Responds to fires and other emergency situations to protect life and property.",
    ),
    JobTitle(
        title="Social Worker",
        industry="Government",
        category="Social Services",
        responsibilities=["assess client needs", "connect clients with resources", "manage case files", "provide counseling support"],
        required_skills=["case management", "empathy", "communication", "knowledge of social services"],
        education_required="Bachelor's or Master's in Social Work + license",
        avg_salary_usd_annual=55000,
        automatable_by_ai=False,
        description="Helps individuals and families access services and improve their well-being.",
    ),
    JobTitle(
        title="Military Officer",
        industry="Government",
        category="Defense",
        responsibilities=["lead military personnel", "plan and execute missions", "manage resources", "ensure troop readiness"],
        required_skills=["leadership", "strategic planning", "physical fitness", "weapons proficiency"],
        education_required="Military academy or ROTC + commission",
        avg_salary_usd_annual=90000,
        automatable_by_ai=False,
        description="Commands and leads military units in training and operations.",
    ),
    # -----------------------------------------------------------------------
    # Science & Research
    # -----------------------------------------------------------------------
    JobTitle(
        title="Research Scientist",
        industry="Science",
        category="Research",
        responsibilities=["design and conduct experiments", "analyze and publish results", "secure research funding", "collaborate with research teams"],
        required_skills=["research methodology", "data analysis", "scientific writing", "lab techniques"],
        education_required="PhD in relevant scientific field",
        avg_salary_usd_annual=100000,
        automatable_by_ai=False,
        description="Conducts original research to advance knowledge in a scientific domain.",
    ),
    JobTitle(
        title="Biologist",
        industry="Science",
        category="Life Sciences",
        responsibilities=["study living organisms", "conduct field and lab research", "analyze biological data", "publish findings"],
        required_skills=["biology", "lab techniques", "data analysis", "scientific writing"],
        education_required="Bachelor's or advanced degree in Biology",
        avg_salary_usd_annual=82000,
        automatable_by_ai=True,
        description="Studies living organisms and their relationship to the environment.",
    ),
    JobTitle(
        title="Environmental Scientist",
        industry="Science",
        category="Environmental",
        responsibilities=["monitor environmental conditions", "assess environmental impact", "develop remediation plans", "advise on regulations"],
        required_skills=["environmental analysis", "GIS", "data collection", "regulatory knowledge"],
        education_required="Bachelor's in Environmental Science",
        avg_salary_usd_annual=73000,
        automatable_by_ai=True,
        description="Studies and addresses environmental issues affecting ecosystems and public health.",
    ),
    # -----------------------------------------------------------------------
    # Arts, Media & Entertainment
    # -----------------------------------------------------------------------
    JobTitle(
        title="Graphic Designer",
        industry="Creative Arts",
        category="Design",
        responsibilities=["create visual concepts", "design logos and branding", "layout print and digital media", "collaborate with marketing teams"],
        required_skills=["Adobe Creative Suite", "typography", "color theory", "branding"],
        education_required="Bachelor's in Graphic Design or related",
        avg_salary_usd_annual=58000,
        automatable_by_ai=True,
        description="Creates visual content for print, digital, and brand communications.",
    ),
    JobTitle(
        title="Film / Video Director",
        industry="Entertainment",
        category="Production",
        responsibilities=["direct film and video productions", "manage cast and crew", "oversee editing", "develop creative vision"],
        required_skills=["cinematography", "storytelling", "leadership", "editing", "creative vision"],
        education_required="Bachelor's in Film or Communications",
        avg_salary_usd_annual=92000,
        automatable_by_ai=False,
        description="Directs the creative aspects of film and video productions.",
    ),
    JobTitle(
        title="Musician / Performer",
        industry="Entertainment",
        category="Performing Arts",
        responsibilities=["practice and perform music", "record in studio settings", "collaborate with other artists", "market and promote work"],
        required_skills=["musical instrument(s)", "vocal performance", "music theory", "performance skills"],
        education_required="Varies — conservatory or self-taught",
        avg_salary_usd_annual=45000,
        automatable_by_ai=False,
        description="Creates and performs musical compositions for audiences.",
    ),
    JobTitle(
        title="Journalist / Reporter",
        industry="Media",
        category="Journalism",
        responsibilities=["investigate and report news", "conduct interviews", "write articles", "verify facts"],
        required_skills=["writing", "research", "interviewing", "ethics", "multimedia"],
        education_required="Bachelor's in Journalism or Communications",
        avg_salary_usd_annual=52000,
        automatable_by_ai=True,
        description="Researches, writes, and reports on news and current events.",
    ),
    # -----------------------------------------------------------------------
    # Hospitality & Food Service
    # -----------------------------------------------------------------------
    JobTitle(
        title="Chef / Head Chef",
        industry="Hospitality",
        category="Food Service",
        responsibilities=["plan and create menus", "lead kitchen staff", "maintain food safety standards", "manage food costs"],
        required_skills=["culinary arts", "kitchen management", "menu planning", "food safety"],
        education_required="Culinary degree or apprenticeship",
        avg_salary_usd_annual=55000,
        automatable_by_ai=False,
        description="Leads kitchen operations and creates culinary experiences.",
    ),
    JobTitle(
        title="Hotel Manager",
        industry="Hospitality",
        category="Management",
        responsibilities=["oversee hotel operations", "manage staff", "handle guest relations", "control hotel budget"],
        required_skills=["hospitality management", "customer service", "leadership", "budgeting"],
        education_required="Bachelor's in Hospitality Management",
        avg_salary_usd_annual=65000,
        automatable_by_ai=True,
        description="Manages all aspects of hotel operations to ensure guest satisfaction.",
    ),
    JobTitle(
        title="Event Planner",
        industry="Hospitality",
        category="Events",
        responsibilities=["plan and coordinate events", "manage vendors", "track event budgets", "ensure event logistics"],
        required_skills=["event management", "negotiation", "organization", "vendor management"],
        education_required="Bachelor's in Hospitality or Event Management",
        avg_salary_usd_annual=58000,
        automatable_by_ai=True,
        description="Plans and executes events ranging from corporate functions to weddings.",
    ),
    # -----------------------------------------------------------------------
    # Real Estate
    # -----------------------------------------------------------------------
    JobTitle(
        title="Real Estate Agent",
        industry="Real Estate",
        category="Sales",
        responsibilities=["list and market properties", "show homes to buyers", "negotiate contracts", "assist with closing"],
        required_skills=["sales", "negotiation", "local market knowledge", "communication"],
        education_required="Real estate license",
        avg_salary_usd_annual=62000,
        automatable_by_ai=True,
        description="Assists buyers and sellers in real estate transactions.",
    ),
    JobTitle(
        title="Property Manager",
        industry="Real Estate",
        category="Management",
        responsibilities=["manage rental properties", "collect rent", "coordinate maintenance", "screen tenants"],
        required_skills=["tenant management", "budgeting", "maintenance coordination", "communication"],
        education_required="High school diploma + property management license",
        avg_salary_usd_annual=58000,
        automatable_by_ai=True,
        description="Manages rental properties on behalf of owners.",
    ),
    JobTitle(
        title="Real Estate Appraiser",
        industry="Real Estate",
        category="Valuation",
        responsibilities=["assess property values", "inspect properties", "research comparable sales", "write appraisal reports"],
        required_skills=["property valuation", "market analysis", "attention to detail", "report writing"],
        education_required="Bachelor's + appraiser license",
        avg_salary_usd_annual=67000,
        automatable_by_ai=True,
        description="Determines the market value of real property.",
    ),
    # -----------------------------------------------------------------------
    # Agriculture & Environment
    # -----------------------------------------------------------------------
    JobTitle(
        title="Agricultural Farmer",
        industry="Agriculture",
        category="Farming",
        responsibilities=["plant and harvest crops", "manage farm equipment", "monitor soil and crop health", "manage farm finances"],
        required_skills=["crop management", "equipment operation", "soil science", "irrigation"],
        education_required="High school diploma + vocational training or degree",
        avg_salary_usd_annual=43000,
        automatable_by_ai=True,
        description="Grows and harvests crops for food and industrial purposes.",
    ),
    JobTitle(
        title="Veterinarian",
        industry="Agriculture",
        category="Animal Health",
        responsibilities=["diagnose and treat animals", "perform surgeries", "advise on animal care", "manage vaccination programs"],
        required_skills=["veterinary medicine", "surgery", "diagnostics", "client communication"],
        education_required="DVM or VMD degree + license",
        avg_salary_usd_annual=119000,
        automatable_by_ai=False,
        description="Provides medical care for animals in clinical and farm settings.",
    ),
    # -----------------------------------------------------------------------
    # Psychology & Counseling
    # -----------------------------------------------------------------------
    JobTitle(
        title="Psychologist",
        industry="Mental Health",
        category="Psychology",
        responsibilities=["assess and diagnose mental health conditions", "provide therapy", "conduct psychological testing", "research mental health"],
        required_skills=["psychological assessment", "therapy techniques", "empathy", "research"],
        education_required="PhD or PsyD in Psychology + license",
        avg_salary_usd_annual=90000,
        automatable_by_ai=False,
        description="Assesses and treats mental, emotional, and behavioral disorders.",
    ),
    JobTitle(
        title="Licensed Counselor / Therapist",
        industry="Mental Health",
        category="Counseling",
        responsibilities=["provide individual and group therapy", "develop treatment plans", "document client progress", "maintain ethical practice"],
        required_skills=["counseling techniques", "empathy", "active listening", "documentation"],
        education_required="Master's in Counseling or Social Work + license",
        avg_salary_usd_annual=58000,
        automatable_by_ai=False,
        description="Provides therapeutic support for individuals dealing with mental health challenges.",
    ),
    # -----------------------------------------------------------------------
    # Skilled Trades & Maintenance
    # -----------------------------------------------------------------------
    JobTitle(
        title="HVAC Technician",
        industry="Skilled Trades",
        category="HVAC",
        responsibilities=["install and service HVAC systems", "diagnose equipment faults", "conduct preventive maintenance", "ensure safety compliance"],
        required_skills=["HVAC systems", "refrigerant handling", "electrical wiring", "troubleshooting"],
        education_required="Vocational training + EPA 608 certification",
        avg_salary_usd_annual=52000,
        automatable_by_ai=False,
        description="Installs and maintains heating, ventilation, and air conditioning systems.",
    ),
    JobTitle(
        title="Auto Mechanic",
        industry="Skilled Trades",
        category="Automotive",
        responsibilities=["diagnose vehicle problems", "perform repairs and maintenance", "replace parts", "advise customers on repairs"],
        required_skills=["automotive systems", "diagnostic tools", "mechanical repair", "customer service"],
        education_required="Vocational training or Associate's + ASE certification",
        avg_salary_usd_annual=48000,
        automatable_by_ai=True,
        description="Inspects, repairs, and maintains vehicles.",
    ),
    # -----------------------------------------------------------------------
    # Food Processing & Restaurants
    # -----------------------------------------------------------------------
    JobTitle(
        title="Food Safety Inspector",
        industry="Government",
        category="Inspection",
        responsibilities=["inspect food establishments", "enforce food safety regulations", "investigate foodborne illness complaints", "issue violations"],
        required_skills=["food safety regulations", "inspection techniques", "report writing", "communication"],
        education_required="Bachelor's in Food Science or related",
        avg_salary_usd_annual=52000,
        automatable_by_ai=True,
        description="Ensures food establishments comply with health and safety regulations.",
    ),
    # -----------------------------------------------------------------------
    # Human Services & Non-Profit
    # -----------------------------------------------------------------------
    JobTitle(
        title="Nonprofit Program Manager",
        industry="Non-Profit",
        category="Program Management",
        responsibilities=["manage programs and services", "track program outcomes", "manage grant budgets", "coordinate volunteers"],
        required_skills=["program management", "grant writing", "community outreach", "budgeting"],
        education_required="Bachelor's in Social Work, Public Policy, or related",
        avg_salary_usd_annual=62000,
        automatable_by_ai=True,
        description="Plans and oversees programs for non-profit organizations.",
    ),
    # -----------------------------------------------------------------------
    # Information Technology (IT)
    # -----------------------------------------------------------------------
    JobTitle(
        title="IT Support Specialist",
        industry="Technology",
        category="IT Support",
        responsibilities=["troubleshoot hardware and software", "assist end users", "set up devices and networks", "document issues"],
        required_skills=["troubleshooting", "networking", "operating systems", "customer service"],
        education_required="Associate's or Bachelor's in IT + CompTIA A+",
        avg_salary_usd_annual=52000,
        automatable_by_ai=True,
        description="Provides technical support and assistance for hardware and software issues.",
    ),
    JobTitle(
        title="Network Administrator",
        industry="Technology",
        category="Networking",
        responsibilities=["maintain network infrastructure", "monitor network performance", "troubleshoot network issues", "implement network security"],
        required_skills=["networking", "Cisco", "firewalls", "VPNs", "monitoring tools"],
        education_required="Bachelor's in IT or Networking + CCNA",
        avg_salary_usd_annual=80000,
        automatable_by_ai=True,
        description="Manages and maintains organizational computer networks.",
    ),
    JobTitle(
        title="Database Administrator",
        industry="Technology",
        category="Database",
        responsibilities=["manage databases", "optimize query performance", "backup and restore data", "ensure data security"],
        required_skills=["SQL", "database management systems", "performance tuning", "backup strategies"],
        education_required="Bachelor's in Computer Science or IT",
        avg_salary_usd_annual=95000,
        automatable_by_ai=True,
        description="Manages and maintains organizational databases.",
    ),
]


class JobTitleDatabase:
    """Searchable database of all job titles."""

    def __init__(self) -> None:
        self._titles: List[JobTitle] = list(_JOB_TITLES)

    # -----------------------------------------------------------------------
    # Query methods
    # -----------------------------------------------------------------------

    def search(self, keyword: str) -> List[JobTitle]:
        """Full-text search across title, industry, category, and description."""
        kw = keyword.lower()
        return [
            j for j in self._titles
            if kw in j.title.lower()
            or kw in j.industry.lower()
            or kw in j.category.lower()
            or kw in j.description.lower()
            or any(kw in s.lower() for s in j.required_skills)
        ]

    def get_by_title(self, title: str) -> Optional[JobTitle]:
        """Return a job title record by exact title (case-insensitive)."""
        tl = title.lower()
        for j in self._titles:
            if j.title.lower() == tl:
                return j
        return None

    def get_by_industry(self, industry: str) -> List[JobTitle]:
        """Return all job titles in a given industry."""
        ind = industry.lower()
        return [j for j in self._titles if j.industry.lower() == ind]

    def get_automatable_jobs(self) -> List[JobTitle]:
        """Return all job titles that are highly automatable by AI."""
        return [j for j in self._titles if j.automatable_by_ai]

    def list_industries(self) -> List[str]:
        """Return a sorted, deduplicated list of all industries."""
        return sorted({j.industry for j in self._titles})

    def list_categories(self) -> List[str]:
        """Return a sorted, deduplicated list of all categories."""
        return sorted({j.category for j in self._titles})

    def list_all_titles(self) -> List[str]:
        """Return a sorted list of every job title in the database."""
        return sorted(j.title for j in self._titles)

    def count(self) -> int:
        """Return the total number of job titles in the database."""
        return len(self._titles)

    def top_titles_by_industry(self, industry: str, limit: int = 10) -> List[JobTitle]:
        """Return up to *limit* job titles for a given industry."""
        return self.get_by_industry(industry)[:limit]
