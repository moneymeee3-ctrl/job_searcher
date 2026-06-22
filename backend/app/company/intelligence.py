"""EMBEDHUNT AI — Company Intelligence Registry"""
from dataclasses import dataclass
from enum import Enum

class CompanyTier(str, Enum):
    TIER1_SEMICONDUCTOR="tier1_semiconductor"; TIER2_AUTOMOTIVE="tier2_automotive"
    TIER3_INDUSTRIAL="tier3_industrial"; TIER4_TELECOM="tier4_telecom"
    TIER5_CONSUMER="tier5_consumer"; TIER6_DEFENSE="tier6_defense"; INDIA_FOCUSED="india_focused"

@dataclass(frozen=True)
class CompanyTarget:
    name: str; tier: CompanyTier; careers_url: str; india_office: bool=True; priority: int=50

REGISTRY: list[CompanyTarget] = [
    CompanyTarget("Qualcomm",CompanyTier.TIER1_SEMICONDUCTOR,"https://careers.qualcomm.com",priority=99),
    CompanyTarget("Intel",CompanyTier.TIER1_SEMICONDUCTOR,"https://jobs.intel.com",priority=98),
    CompanyTarget("NVIDIA",CompanyTier.TIER1_SEMICONDUCTOR,"https://nvidia.wd5.myworkdayjobs.com",priority=98),
    CompanyTarget("AMD",CompanyTier.TIER1_SEMICONDUCTOR,"https://jobs.amd.com",priority=97),
    CompanyTarget("NXP Semiconductors",CompanyTier.TIER1_SEMICONDUCTOR,"https://careers.nxp.com",priority=96),
    CompanyTarget("Infineon",CompanyTier.TIER1_SEMICONDUCTOR,"https://www.infineon.com/careers",priority=95),
    CompanyTarget("Texas Instruments",CompanyTier.TIER1_SEMICONDUCTOR,"https://careers.ti.com",priority=95),
    CompanyTarget("STMicroelectronics",CompanyTier.TIER1_SEMICONDUCTOR,"https://www.st.com/careers",priority=94),
    CompanyTarget("Microchip",CompanyTier.TIER1_SEMICONDUCTOR,"https://careers.microchip.com",priority=93),
    CompanyTarget("Renesas",CompanyTier.TIER1_SEMICONDUCTOR,"https://www.renesas.com/careers",priority=93),
    CompanyTarget("Analog Devices",CompanyTier.TIER1_SEMICONDUCTOR,"https://careers.analog.com",priority=92),
    CompanyTarget("Broadcom",CompanyTier.TIER1_SEMICONDUCTOR,"https://careers.broadcom.com",priority=90),
    CompanyTarget("ARM",CompanyTier.TIER1_SEMICONDUCTOR,"https://careers.arm.com",priority=90),
    CompanyTarget("MediaTek",CompanyTier.TIER1_SEMICONDUCTOR,"https://careers.mediatek.com",priority=89),
    CompanyTarget("Marvell",CompanyTier.TIER1_SEMICONDUCTOR,"https://jobs.marvell.com",priority=88),
    CompanyTarget("Silicon Labs",CompanyTier.TIER1_SEMICONDUCTOR,"https://jobs.silabs.com",priority=87),
    CompanyTarget("Nordic Semiconductor",CompanyTier.TIER1_SEMICONDUCTOR,"https://www.nordicsemi.com/careers",priority=86),
    CompanyTarget("ON Semiconductor",CompanyTier.TIER1_SEMICONDUCTOR,"https://onsemi.com/careers",priority=85),
    CompanyTarget("Synaptics",CompanyTier.TIER1_SEMICONDUCTOR,"https://www.synaptics.com/company/careers",priority=84),
    CompanyTarget("Cadence",CompanyTier.TIER1_SEMICONDUCTOR,"https://cadence.com/careers",priority=83),
    CompanyTarget("Synopsys",CompanyTier.TIER1_SEMICONDUCTOR,"https://synopsys.com/careers",priority=83),
    CompanyTarget("Realtek",CompanyTier.TIER1_SEMICONDUCTOR,"https://www.realtek.com/careers",priority=80),
    CompanyTarget("CEVA",CompanyTier.TIER1_SEMICONDUCTOR,"https://www.ceva-dsp.com/careers",priority=78),
    CompanyTarget("MosChip",CompanyTier.TIER1_SEMICONDUCTOR,"https://moschip.com/careers",priority=75),
    CompanyTarget("Bosch",CompanyTier.TIER2_AUTOMOTIVE,"https://www.bosch.com/careers",priority=90),
    CompanyTarget("Bosch Global Software",CompanyTier.TIER2_AUTOMOTIVE,"https://jobs.bosch-softwaretechnologies.com",priority=85),
    CompanyTarget("Continental",CompanyTier.TIER2_AUTOMOTIVE,"https://jobs.continental.com",priority=89),
    CompanyTarget("Valeo",CompanyTier.TIER2_AUTOMOTIVE,"https://valeo.com/en/careers",priority=87),
    CompanyTarget("ZF Group",CompanyTier.TIER2_AUTOMOTIVE,"https://jobs.zf.com",priority=86),
    CompanyTarget("Aptiv",CompanyTier.TIER2_AUTOMOTIVE,"https://aptiv.com/en/careers",priority=87),
    CompanyTarget("Harman",CompanyTier.TIER2_AUTOMOTIVE,"https://harman.com/careers",priority=86),
    CompanyTarget("KPIT",CompanyTier.TIER2_AUTOMOTIVE,"https://kpit.com/careers",priority=88),
    CompanyTarget("Tata Technologies",CompanyTier.TIER2_AUTOMOTIVE,"https://tatatechnologies.com/careers",priority=85),
    CompanyTarget("LTTS",CompanyTier.TIER2_AUTOMOTIVE,"https://ltts.com/careers",priority=84),
    CompanyTarget("Cyient",CompanyTier.TIER2_AUTOMOTIVE,"https://cyient.com/careers",priority=82),
    CompanyTarget("Denso",CompanyTier.TIER2_AUTOMOTIVE,"https://densocareers.com",priority=82),
    CompanyTarget("Magna",CompanyTier.TIER2_AUTOMOTIVE,"https://magna.com/careers",priority=83),
    CompanyTarget("Siemens",CompanyTier.TIER3_INDUSTRIAL,"https://jobs.siemens.com",priority=82),
    CompanyTarget("ABB",CompanyTier.TIER3_INDUSTRIAL,"https://careers.abb.com",priority=80),
    CompanyTarget("Honeywell",CompanyTier.TIER3_INDUSTRIAL,"https://careers.honeywell.com",priority=80),
    CompanyTarget("Schneider Electric",CompanyTier.TIER3_INDUSTRIAL,"https://careers.se.com",priority=78),
    CompanyTarget("Rockwell Automation",CompanyTier.TIER3_INDUSTRIAL,"https://rockwellautomation.com/careers",priority=76),
    CompanyTarget("Cisco",CompanyTier.TIER4_TELECOM,"https://jobs.cisco.com",priority=85),
    CompanyTarget("Ericsson",CompanyTier.TIER4_TELECOM,"https://jobs.ericsson.com",priority=82),
    CompanyTarget("Nokia",CompanyTier.TIER4_TELECOM,"https://careers.nokia.com",priority=81),
    CompanyTarget("Juniper Networks",CompanyTier.TIER4_TELECOM,"https://juniper.net/careers",priority=79),
    CompanyTarget("Samsung",CompanyTier.TIER5_CONSUMER,"https://samsung.com/global/careers",priority=83),
    CompanyTarget("Apple",CompanyTier.TIER5_CONSUMER,"https://jobs.apple.com",priority=82),
    CompanyTarget("Dyson",CompanyTier.TIER5_CONSUMER,"https://careers.dyson.com",priority=74),
    CompanyTarget("Collins Aerospace",CompanyTier.TIER6_DEFENSE,"https://jobs.collinsaerospace.com",priority=75),
    CompanyTarget("Thales",CompanyTier.TIER6_DEFENSE,"https://thalesgroup.com/careers",priority=74),
    CompanyTarget("Tata Elxsi",CompanyTier.INDIA_FOCUSED,"https://tataelxsi.com/careers",priority=86),
    CompanyTarget("Mindgrove Technologies",CompanyTier.INDIA_FOCUSED,"https://mindgrove.ai/careers",priority=80),
    CompanyTarget("L&T Technology Services",CompanyTier.INDIA_FOCUSED,"https://ltts.com/careers",priority=82),
    CompanyTarget("Qualcomm India",CompanyTier.INDIA_FOCUSED,"https://careers.qualcomm.com",priority=97),
    CompanyTarget("NVIDIA India",CompanyTier.INDIA_FOCUSED,"https://nvidia.wd5.myworkdayjobs.com",priority=95),
]

JOB_PORTALS = [
    {"name":"Instahyre","url":"https://instahyre.com","priority":95},
    {"name":"Cutshort","url":"https://cutshort.io","priority":93},
    {"name":"Wellfound","url":"https://wellfound.com","priority":90},
    {"name":"LinkedIn Jobs","url":"https://linkedin.com/jobs","priority":88},
    {"name":"Naukri","url":"https://naukri.com","priority":85},
    {"name":"IIMJobs","url":"https://iimjobs.com","priority":82},
    {"name":"Hirist","url":"https://hirist.tech","priority":80},
    {"name":"Indeed","url":"https://indeed.co.in","priority":80},
    {"name":"Foundit","url":"https://foundit.in","priority":78},
    {"name":"TimesJobs","url":"https://timesjobs.com","priority":70},
    {"name":"FlexJobs","url":"https://flexjobs.com","priority":65},
    {"name":"Remote OK","url":"https://remoteok.com","priority":64},
    {"name":"We Work Remotely","url":"https://weworkremotely.com","priority":62},
]

EMBEDDED_JOB_TITLES = [
    "Embedded Software Engineer","Embedded Software Developer","Embedded C Developer",
    "Firmware Engineer","BSP Engineer","Device Driver Engineer","Linux Embedded Engineer",
    "AUTOSAR Engineer","RTOS Engineer","Automotive Software Engineer","ECU Software Engineer",
    "Functional Safety Engineer","IoT Firmware Engineer","DSP Engineer","Bootloader Engineer",
    "Low Level Software Engineer","Middleware Engineer","Embedded Linux Developer","SoC Engineer",
]

def get_ordered_companies(): return sorted(REGISTRY, key=lambda c: c.priority, reverse=True)
def get_by_tier(tier: CompanyTier): return [c for c in REGISTRY if c.tier == tier]
