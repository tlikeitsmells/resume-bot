import os
import random

HOSPITALITY_SKILLS = {
    "restaurant manager": [
        "Team leadership","Scheduling","Guest recovery","P&L oversight","Labor forecasting",
        "Inventory control","Vendor management","Food safety (ServSafe)","POS management","Training & onboarding",
        "Service standards","Table turns optimization","Reservation management","Event coordination"
    ],
    "front of house manager": [
        "Floor management","Guest relations","Upselling","Waitlist & seating","Wine & beverage knowledge",
        "Cash handling","Conflict resolution","Training","Opening/closing procedures","Health code compliance"
    ],
    "chef": [
        "Menu development","Costing & margins","Supplier negotiation","Line management","Prep workflows",
        "Waste reduction","Food safety (HACCP)","Inventory & ordering","Seasonal sourcing","Recipe standardization"
    ],
    "sous chef": [
        "Expediting","Station training","Prep planning","Ordering","Inventory counts","Waste control",
        "Recipe scaling","Allergen controls","Line checks","Quality control"
    ],
    "line cook": [
        "Station setup & breakdown","Recipe execution","Consistency","Sanitation","Ticket timing",
        "Knife skills","Food safety","High-volume service","Prep efficiency","Waste minimization"
    ],
    "bar manager": [
        "Cocktail program","Cost control","Supplier relations","Staff training","Inventory & counts",
        "POS programming","Compliance (ID & service)","Event menus","Waste control","Guest experience"
    ]
}

GENERIC_SKILLS = [
    "Process improvement","Cross-functional collaboration","Documentation","KPI tracking","Data-driven decisions",
    "Project management","Stakeholder management","Training & enablement","SOP creation","Quality assurance"
]

BULLET_PATTERNS = [
    "Increased {metric}% {kpi} by {action} using {tool}, improving {impact}.",
    "Reduced {kpi} by {metric}% through {action}, resulting in {impact}.",
    "Implemented {tool} to {action}, driving {metric}% improvement in {kpi}.",
    "Standardized {process} and trained {count}+ staff, cutting {kpi} by {metric}% and boosting {impact}.",
    "Optimized {process} via {action}, {metric}% better {kpi} and enhanced {impact}."
]

HOSPITALITY_KPIS = ["ticket time","COGS","labor cost","guest wait time","table turns","waste","voids/comp","check average"]
HOSPITALITY_TOOLS = ["POS","inventory sheet","prep list","par levels","HACCP logs","reservation system"]
HOSPITALITY_ACTIONS = ["retraining staff on standards","reworking pars","tightening prep workflows","revamping mise en place",
                       "introducing station checklists","rebalancing floor plan","adding pre-shift huddles"]
HOSPITALITY_IMPACT = ["guest satisfaction","review scores","health-score readiness","shift consistency","profitability"]

def suggest_skills(role:str):
    r = (role or "").lower()
    for key, vals in HOSPITALITY_SKILLS.items():
        if key in r:
            return vals + GENERIC_SKILLS[:5]
    return GENERIC_SKILLS

def suggest_bullets(role:str, count:int=5):
    import random
    bullets = []
    for _ in range(count):
        patt = random.choice(BULLET_PATTERNS)
        b = patt.format(
            metric=random.choice([8,10,12,15,18,20,25,30,35]),
            kpi=random.choice(HOSPITALITY_KPIS),
            action=random.choice(HOSPITALITY_ACTIONS),
            tool=random.choice(HOSPITALITY_TOOLS),
            impact=random.choice(HOSPITALITY_IMPACT),
            process=random.choice(["opening/closing","inventory counts","line setup","expediting","ordering"]),
            count=random.choice([4,6,8,10,12])
        )
        if not b.endswith("."): b += "."
        bullets.append(b)
    return bullets

def refine_with_openai(prompt:str, items:list):
    # No OpenAI dependency here; PythonAnywhere-friendly. You can integrate your own later.
    return items
