#!/usr/bin/env python3



import requests
import time
import os
import re  # For text cleaning and formatting
from datetime import datetime
from bs4 import BeautifulSoup
import wikipediaapi


def get_wikipedia_articles():
    """Download articles from Wikipedia about nuclear power"""
    print("Getting Wikipedia articles...")


    # Set up Wikipedia
    wiki = wikipediaapi.Wikipedia(
        language='en',
        user_agent='NuclearLearningBot/1.0 (Educational)'
    )

    # COMPREHENSIVE list of nuclear topics organized by category. I based this on curriculum and past experience

    nuclear_categories = {
        "reactor_fundamentals": [
            # Core Concepts
            "Nuclear reactor", "Nuclear fission", "Nuclear chain reaction",
            "Critical mass", "Criticality (nuclear)", "Neutron", "Control rod",
            "Nuclear fuel", "Reactor core", "Reactor physics",
            "Neutron poison", "Neutron flux", "Reactor kinetics",
            "Nuclear cross section", "Neutron multiplication factor",
            "Six-factor formula", "Xenon poisoning", "Samarium poisoning",
            "Prompt neutron", "Delayed neutron", "Effective multiplication factor",
            "Reactivity (nuclear engineering)", "Reactor period", "Doppler broadening",
            "Moderator (nuclear physics)", "Coolant (nuclear reactor)", "Neutron reflector",
            "Gamma ray", "Alpha particle", "Beta particle", "Ionizing radiation",
            "Binding energy", "Mass defect", "Fission product", "Isotope",
            "Decay heat", "Thermal neutron", "Fast neutron", "Neutron diffusion",
            "Diffusion length", "Fermi age", "Four-factor formula",
            "Neutron capture", "Nuclear scattering", "Resonance integral",
            "Reactor startup", "Reactor shutdown", "Core damage", "Nuclear safety principle",
            "Reactor control theory", "Subcritical multiplication", "Startup rate",
            "Effective delayed neutron fraction", "Neutron generation time",
            "Moderator temperature coefficient", "Fuel temperature coefficient",
            "Power coefficient (nuclear reactor)", "Differential boron worth",
            "Shutdown margin", "K-excess", "Burnable poison", "Fuel depletion",
            "Control rod worth", "Axial power distribution", "Radial power distribution",
            "Quadrant power tilt", "Fuel burnup", "Zirconium hydride",
            "Atomic nucleus", "Subatomic particle", "Electron", "Proton", "Atomic number",
            "Mass number", "Atomic mass unit", "Nuclear binding energy",
            "Nuclear isomer", "Radioisotope", "Half-life", "Mean lifetime", "Decay chain",
            "Radioactivity", "Activity (radioactivity)", "Curie", "Becquerel",
            "Roentgen", "Rad (unit)", "Rem (unit)", "Sievert", "Gray (unit)",
            "Radiation dosimetry", "Neutron activation", "Nuclear transmutation"
        ],

        "reactor_types": [
            "Pressurized water reactor", "Boiling water reactor",
            "Light-water reactor", "Heavy-water reactor",
            "Nuclear reactor technology", "Generation II reactor",
            "Generation III reactor", "Advanced boiling water reactor",
            "AP1000", "Economic Simplified Boiling Water Reactor",
            "Small modular reactor", "Fast breeder reactor", "Molten salt reactor",
            "High-temperature gas-cooled reactor", "Liquid metal fast breeder reactor",
            "CANDU reactor", "VVER", "RBMK", "Magnox", "AGR (reactor)",
            "Fusion power", "Tokamak", "Stellarator", "ITER",
            "Research reactor", "Nuclear propulsion", "Submarine (nuclear)",
            "Floating nuclear power plant", "Microreactor", "Generation IV reactor",
            "Advanced reactor", "Nuclear power plant design", "Reactor cooling system",
            "Reactor safety systems", "Reactor core isolation cooling",
            "Passive safety system", "Active safety system", "Containment building",
            "Pressure vessel", "Steam generator (nuclear power)", "Heat exchanger",
            "Turbine", "Electric generator", "Condenser (heat transfer)",
            "Cooling tower", "Reactor building", "Fuel assembly"
        ],

        "plant_systems": [
            "Reactor pressure vessel", "Steam generator (nuclear power)",
            "Nuclear reactor coolant", "Emergency core cooling system",
            "Reactor protection system", "Containment building",
            "Nuclear reactor safety system", "Reactor scram",
            "Reactor coolant pump", "Pressurizer", "Steam turbine",
            "Condenser (heat transfer)", "Feedwater system",
            "Auxiliary feedwater system", "Residual heat removal",
            "Off-gas system", "Spent fuel pool", "Control valve", "Check valve",
            "Relief valve", "Safety valve", "Gate valve", "Globe valve",
            "Ball valve", "Butterfly valve", "Motor-operated valve",
            "Heat exchanger", "Piping and plumbing fitting", "Pump",
            "Centrifugal pump", "Positive displacement pump", "Axial-flow pump",
            "Main steam system", "Cooling water system", "Lube oil system",
            "Chemical and volume control system", "Boron recycle system",
            "Waste management system (nuclear)", "Reactor water cleanup system (BWR)",
            "Fire protection system", "Emergency power system", "Uninterruptible power supply",
            "Control room (nuclear power)", "Human-machine interface", "Distributed control system"
        ],

        "safety_systems": [
            "Nuclear safety", "Defense in depth (nuclear engineering)",
            "Nuclear reactor safety system", "Passive nuclear safety",
            "Emergency core cooling system", "Containment",
            "Reactor protection system", "Safety injection",
            "Isolation condenser", "Reactor core isolation cooling",
            "Accident tolerant fuels", "Emergency diesel generator",
            "Emergency preparedness (nuclear power)", "Nuclear security",
            "Fire protection system (nuclear)", "Safety culture (nuclear power)",
            "Human factors (safety)", "Design basis accident", "Beyond design basis accident",
            "Severe accident management", "Core-melt accident", "Loss-of-coolant accident",
            "Steam generator tube rupture", "Main steam line break", "Feedwater line break",
            "Control rod ejection accident", "Anticipated transient without scram (ATWS)",
            "Station blackout", "Loss of off-site power", "Safety function (nuclear power)",
            "Critical safety function", "Reactor trip system", "Engineered safety features"
        ],

        "operations_safety": [
            "Nuclear reactor operator", "Nuclear reactor safety",
            "Nuclear meltdown", "Loss-of-coolant accident",
            "Nuclear reactor accident", "Reactor scram",
            "Three Mile Island accident", "Chernobyl disaster",
            "Fukushima Daiichi nuclear disaster", "Nuclear safety culture",
            "Human factors in nuclear safety", "Operational event",
            "Licensee (nuclear power)", "Technical specifications (nuclear power plant)",
            "10 CFR Part 50", "10 CFR Part 55", "NUREG",
            "Control room (nuclear power)", "Operating experience (nuclear)",
            "Corrective action program (nuclear)", "Procedure (nuclear power)",
            "Training (nuclear power plant)", "Simulator (training)",
            "Shift supervisor (nuclear)", "Radiation protection program",
            "ALARA", "Contamination control", "Radiological survey",
            "Emergency operating procedures (EOPs)", "Abnormal operating procedures (AOPs)",
            "Surveillance testing (nuclear)", "Maintenance (nuclear power plant)"
        ],

        "regulatory_licensing": [
            "Nuclear Regulatory Commission", "Nuclear reactor licensing",
            "Nuclear operator licensing", "Technical specifications (nuclear power plant)",
            "10 CFR Part 50", "10 CFR Part 55", "NUREG",
            "Nuclear safety analysis", "Probabilistic risk assessment",
            "Inservice inspection", "Reactor oversight process", "Regulatory guide (NRC)",
            "NRC Generic Fundamentals Examination", "Atomic Energy Act of 1954",
            "Energy Reorganization Act of 1974", "NRC inspection", "Enforcement (NRC)",
            "Rulemaking (NRC)", "License renewal (nuclear)", "Decommissioning (nuclear)",
            "Quality assurance (nuclear)", "International Atomic Energy Agency (IAEA)",
            "World Association of Nuclear Operators (WANO)", "Operating license (nuclear)"
        ],

        "specific_plants": [
            "Salem Nuclear Power Plant", "Hope Creek Nuclear Generating Station",
            "Vogtle Electric Generating Plant", "Diablo Canyon Power Plant",
            "Byron Nuclear Generating Station", "Braidwood Generating Station",
            "Indian Point Energy Center", "Millstone Nuclear Power Plant",
            "Palo Verde Generating Station", "Browns Ferry Nuclear Plant",
            "Calvert Cliffs Nuclear Power Plant", "Peach Bottom Atomic Power Station",
            "Sequoyah Nuclear Generating Station", "Watts Bar Nuclear Generating Station",
            "Hatch Nuclear Plant", "Grand Gulf Nuclear Generating Station",
            "Arkansas Nuclear One", "Davis-Besse Nuclear Power Station",
            "Perry Nuclear Power Plant", "Oconee Nuclear Station", "Three Mile Island Nuclear Generating Station"
        ],

        "nuclear_science": [
            "Nuclear engineering", "Nuclear thermodynamics", "Heat transfer",
            "Radiation protection", "ALARA", "Nuclear waste", "Spent nuclear fuel",
            "Nuclear fuel cycle", "Uranium enrichment", "Nuclear material",
            "Radioactive decay", "Radiation dosimetry", "Neutron activation",
            "Atomic theory", "Nuclear fusion", "Nuclear binding energy",
            "Half-life", "Decay constant", "Cross section (physics)",
            "Elastic scattering", "Inelastic scattering", "Neutron capture",
            "Fission products", "Transmutation (nuclear physics)",
            "Nuclide", "Stable isotope", "Unstable isotope", "Radioactive series",
            "Alpha decay", "Beta decay", "Electron capture", "Positron emission",
            "Heat transfer coefficient", "Thermal conductivity", "Convection (heat transfer)",
            "Boiling (thermodynamics)", "Critical heat flux", "Steam tables"
        ],

        "instrumentation_control": [
            "Nuclear instrumentation", "Neutron detection",
            "Nuclear reactor control", "Process control",
            "Distributed control system", "Safety system",
            "Reactor protection system", "Emergency diesel generator",
            "Control room (nuclear power)", "Flow sensor", "Pressure sensor",
            "Level sensor", "Temperature sensor", "Differential pressure",
            "Resistance temperature detector", "Thermocouple",
            "Control rod position indicator", "Radiation detector", "Geiger counter",
            "Ionization chamber", "Proportional counter", "Fission chamber",
            "Scintillation counter", "Control loop", "Setpoint (control system)",
            "Human-machine interface (HMI)", "Annunciator", "Control panel"
        ],

        "emergency_response": [
            "Nuclear emergency", "Emergency planning zone",
            "Nuclear accident response", "Evacuation",
            "Potassium iodide", "Radiation emergency",
            "Emergency response organization", "Drill (exercise)",
            "Crisis management", "Accident management (nuclear power)",
            "Emergency classification (nuclear)", "Alert (nuclear emergency)",
            "Site Area Emergency (nuclear)", "General Emergency (nuclear)",
            "Emergency Action Levels (EALs)", "Emergency response facilities (nuclear)",
            "Technical Support Center (TSC)", "Operations Support Center (OSC)",
            "Emergency Operations Facility (EOF)", "Joint Information Center (JIC)",
            "Nuclear Security Event", "Physical protection (nuclear)",
            "Emergency communications (nuclear)", "Public information (nuclear)"
        ]
    }

    # Count total articles we're going to get
    total_articles = sum(len(topics) for topics in nuclear_categories.values())
    current_count = 0

    print(f" Getting {total_articles} articles across {len(nuclear_categories)} categories!")
    print("Categories:")
    for category, topics in nuclear_categories.items():
        print(f"  • {category.replace('_', ' ').title()}: {len(topics)} articles")
    print()

    # Process each category
    all_collected = {}

    for category_name, topics in nuclear_categories.items():
        print(f"Starting category: {category_name.replace('_', ' ').title()}")

        # Create folder for this category
        category_folder = f"data/raw/wikipedia/{category_name}"
        if not os.path.exists(category_folder):
            os.makedirs(category_folder)

        category_collected = 0

        # Get each article in this category
        for topic in topics:
            current_count += 1
            print(f"📄 ({current_count}/{total_articles}) Getting: {topic}")

            try:
                # Get the Wikipedia page
                page = wiki.page(topic)

                # Check if the page exists and has enough content
                if page.exists() and len(page.text) > 500:

                    # Create a safe filename
                    safe_name = topic.replace(" ", "_").replace("(", "").replace(")", "")
                    safe_name = safe_name.replace("/", "_").replace(":", "_")
                    filename = f"{safe_name.lower()}.txt"
                    filepath = os.path.join(category_folder, filename)

                    # Create enhanced content (like your original script!)
                    content = create_enhanced_wikipedia_content(page, category_name)

                    # Save the article to a file
                    with open(filepath, 'w', encoding='utf-8') as file:
                        file.write(content)

                    all_collected[topic] = {
                        'category': category_name,
                        'filepath': filepath,
                        'word_count': len(page.text.split())
                    }
                    category_collected += 1
                    print(f"✅ Saved: {filename}")

                    # Try to get related articles (like your original!)
                    get_related_articles(wiki, page, category_folder, all_collected, topic)

                else:
                    print(f"⚠️ Skipped: {topic} (not found or too short)")

            except Exception as error:
                print(f"❌ Error getting {topic}: {error}")

            # Wait a bit to be nice to Wikipedia's servers
            time.sleep(2)

        print(f"✅ Category {category_name} complete: {category_collected} articles")
        print()

    print(f"🎉 Wikipedia collection finished! Got {len(all_collected)} total articles")
    return all_collected


def create_enhanced_wikipedia_content(page, category):
    """Create enhanced content like your original script"""

    content_sections = []


    header = f"""=== NUCLEAR TRAINING DOCUMENT ===
Title: {page.title}
Source URL: {page.fullurl}
Collection Date: {datetime.now().isoformat()}
Document Type: Nuclear Regulatory/Educational Content
Category: {category.replace('_', ' ').title()}
===================================

"""

    # Add comprehensive summary
    content_sections.append(f"ARTICLE SUMMARY:\n{page.summary}\n")

    # Add main content with better formatting
    main_text = page.text

    # Clean up common Wikipedia formatting issues
    main_text = re.sub(r'\n\s*\n\s*\n', '\n\n', main_text)
    main_text = re.sub(r'=+\s*([^=]+)\s*=+', r'\n\n=== \1 ===\n', main_text)

    content_sections.append(f"FULL ARTICLE CONTENT:\n{main_text}\n")

    # Add categories for context
    if page.categories:
        categories = list(page.categories.keys())[:15]
        content_sections.append(f"RELATED CATEGORIES:\n{chr(10).join(f'- {cat}' for cat in categories)}\n")

    # Add related articles for cross-referencing (like your original!)
    if page.links:
        nuclear_keywords = ['nuclear', 'reactor', 'power', 'steam', 'cooling', 'safety', 'radiation']
        related_links = [link for link in list(page.links.keys())[:25]
                         if any(term in link.lower() for term in nuclear_keywords)]
        if related_links:
            content_sections.append(
                f"RELATED NUCLEAR TOPICS:\n{chr(10).join(f'- {link}' for link in related_links)}\n")

    full_content = header + "\n".join(content_sections)
    return full_content


def get_related_articles(wiki, main_page, category_folder, all_collected, main_topic, max_related=3):
    """Get related articles like your original script"""

    if not main_page.links:
        return

    related_count = 0
    nuclear_keywords = [
        'reactor', 'nuclear', 'power', 'steam', 'cooling', 'safety', 'radiation',
        'control', 'fuel', 'core', 'vessel', 'containment', 'emergency', 'neutron'
    ]

    # Create related folder
    related_folder = os.path.join(category_folder, "related")
    if not os.path.exists(related_folder):
        os.makedirs(related_folder)

    # Look through links for nuclear-related topics
    for link_title in list(main_page.links.keys())[:20]:  # Check first 20 links
        if related_count >= max_related:
            break

        if (link_title not in all_collected and
                any(keyword in link_title.lower() for keyword in nuclear_keywords) and
                len(link_title) < 60 and
                link_title != main_topic):

            try:
                related_page = wiki.page(link_title)
                if (related_page.exists() and
                        len(related_page.text) > 800 and
                        ('nuclear' in related_page.text.lower()[:2000] or
                         'reactor' in related_page.text.lower()[:2000])):
                    # Save the related article
                    safe_name = link_title.replace(" ", "_").replace("(", "").replace(")", "")
                    safe_name = safe_name.replace("/", "_").replace(":", "_")
                    filename = f"related_{safe_name.lower()}.txt"
                    filepath = os.path.join(related_folder, filename)

                    content = create_enhanced_wikipedia_content(related_page, "related")

                    with open(filepath, 'w', encoding='utf-8') as file:
                        file.write(content)

                    all_collected[link_title] = {
                        'category': 'related',
                        'filepath': filepath,
                        'word_count': len(related_page.text.split())
                    }
                    related_count += 1
                    print(f"  📎 Related article: {link_title}")

                    time.sleep(1)  # Rate limiting

            except Exception as error:
                print(f"  ⚠️ Error getting related article '{link_title}': {error}")


def get_nrc_pages():
    """Download pages from NRC website """
    print("Getting NRC documents...")
    print("This will take 10-15 minutes - getting comprehensive regulatory docs!")


    nrc_sources = {
        "operator_licensing": [
            "https://www.nrc.gov/reactors/operator-licensing/",
            "https://www.nrc.gov/reactors/operator-licensing/licensing-process.html",
            "https://www.nrc.gov/reactors/operator-licensing/exam-process.html",
            "https://www.nrc.gov/reading-rm/doc-collections/nuregs/staff/sr1021/",  # Generic Fundamentals
            "https://www.nrc.gov/reading-rm/doc-collections/nuregs/staff/sr1122/",  # Exam Standards
        ],

        "technical_specifications": [
            "https://www.nrc.gov/reactors/operating/licensing/techspecs.html",
            "https://www.nrc.gov/reactors/operating/licensing/techspecs/current-approved-sts.html",
            "https://www.nrc.gov/reading-rm/doc-collections/nuregs/staff/sr1431/",  # Westinghouse PWR STS
            "https://www.nrc.gov/reading-rm/doc-collections/nuregs/staff/sr1433/",  # BWR/4 STS
            "https://www.nrc.gov/reading-rm/doc-collections/nuregs/staff/sr1434/",  # BWR/6 STS
        ],

        "regulatory_guides": [
            "https://www.nrc.gov/reading-rm/doc-collections/nuregs/",
            "https://www.nrc.gov/reading-rm/doc-collections/reg-guides/",
            "https://www.nrc.gov/reading-rm/doc-collections/cfr/part050/",
            "https://www.nrc.gov/reading-rm/doc-collections/cfr/part055/",
            "https://www.nrc.gov/reading-rm/doc-collections/cfr/part020/",  # Radiation Protection
        ],

        "plant_info": [
            "https://www.nrc.gov/info-finder/reactors/salm1.html",  # Salem Unit 1
            "https://www.nrc.gov/info-finder/reactors/salm2.html",  # Salem Unit 2
            "https://www.nrc.gov/info-finder/reactors/hc.html",  # Hope Creek
        ],

        "educational_materials": [
            "https://www.nrc.gov/reading-rm/basic-ref/students/",
            "https://www.nrc.gov/reading-rm/basic-ref/students/for-educators/",
            "https://www.nrc.gov/about-nrc/radiation/",
            "https://www.nrc.gov/reactors/operating/ops-experience/",
            "https://www.nrc.gov/public-involve/citizens/nrc-web-lessons.html",  # Web Lessons
        ],

        "safety_security": [
            "https://www.nrc.gov/about-nrc/radiation/",
            "https://www.nrc.gov/reactors/operating/ops-experience/",
            "https://www.nrc.gov/reactors/operating/licensing/emergency-preparedness.html",
            "https://www.nrc.gov/security/",
            "https://www.nrc.gov/about-nrc/regulatory/enforcement.html",  # Enforcement
        ]
    }

    # Count total URLs
    total_urls = sum(len(urls) for urls in nrc_sources.values())
    current_count = 0

    print(f"📄 Getting {total_urls} NRC documents across {len(nrc_sources)} categories!")

    # Process each category of NRC documents
    nrc_results = []

    for category, urls in nrc_sources.items():
        print(f"📂 Starting NRC category: {category.replace('_', ' ').title()}")

        # Create folder for this category
        nrc_folder = f"data/raw/nrc_documents/{category}"
        if not os.path.exists(nrc_folder):
            os.makedirs(nrc_folder)

        category_success = 0

        # Get each page in this category
        for url in urls:
            current_count += 1
            print(f"({current_count}/{total_urls}) Getting: {url}")

            try:
                # Download the web page with better headers (like your original!)
                headers = {
                    'User-Agent': 'NuclearSROBot/1.0 (Educational Research)',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                }

                response = requests.get(url, timeout=45, headers=headers)

                # Check if download worked
                if response.status_code == 200:

                    # Parse the HTML with better cleaning (like your original!)
                    soup = BeautifulSoup(response.content, 'html.parser')

                    # Get the page title
                    title = soup.find('title')
                    page_title = title.get_text().strip() if title else "NRC Document"

                    # Remove stuff we don't want (like your original!)
                    for unwanted in soup(['script', 'style', 'nav', 'header', 'footer',
                                          'aside', '.navigation', '.sidebar', '.breadcrumb']):
                        unwanted.decompose()

                    # Get main content with better targeting (like your original!)
                    main_content = (soup.find('main') or
                                    soup.find('div', class_='content') or
                                    soup.find('div', id='content') or
                                    soup.find('article') or
                                    soup.body)

                    if main_content:
                        text_content = extract_formatted_text(main_content)
                    else:
                        text_content = soup.get_text(separator='\n', strip=True)

                    # Only save if we got enough content
                    if len(text_content) > 500:

                        # Create enhanced filename
                        filename = create_nrc_filename(url, page_title, category)
                        filepath = os.path.join(nrc_folder, filename)

                        # Create enhanced content
                        content = create_enhanced_nrc_content(text_content, url, page_title, category)

                        # Save the document
                        with open(filepath, 'w', encoding='utf-8') as file:
                            file.write(content)

                        nrc_results.append({
                            'url': url,
                            'category': category,
                            'filepath': filepath,
                            'status': 'success'
                        })
                        category_success += 1
                        print(f"✅ Saved: {filename}")
                    else:
                        print(f"⚠️ Skipped: {url} (not enough content)")
                        nrc_results.append({'url': url, 'status': 'skipped', 'reason': 'too_short'})

                else:
                    print(f"❌ Failed to download {url} (status: {response.status_code})")
                    nrc_results.append({'url': url, 'status': 'error', 'error': f'HTTP {response.status_code}'})

            except Exception as error:
                print(f"❌ Error getting {url}: {error}")
                nrc_results.append({'url': url, 'status': 'error', 'error': str(error)})

            # Wait between downloads (like your original rate limiting!)
            time.sleep(3)

        print(f"✅ NRC category {category} complete: {category_success} documents")
        print()

    successful_nrc = sum(1 for r in nrc_results if r.get('status') == 'success')
    print(f"🎉 NRC collection finished! Got {successful_nrc} documents")
    return nrc_results


def extract_formatted_text(element):
    """Extract well-formatted text from HTML (like your original!)"""

    # Replace headers with formatted versions
    for header in element.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        header_text = header.get_text().strip()
        if header_text:
            header.replace_with(f"\n\n=== {header_text.upper()} ===\n")

    # Replace lists with formatted versions
    for ul in element.find_all('ul'):
        for li in ul.find_all('li'):
            li_text = li.get_text().strip()
            if li_text:
                li.replace_with(f"\n• {li_text}")

    for ol in element.find_all('ol'):
        for i, li in enumerate(ol.find_all('li'), 1):
            li_text = li.get_text().strip()
            if li_text:
                li.replace_with(f"\n{i}. {li_text}")

    # Get text and clean up
    text = element.get_text(separator='\n', strip=True)
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)  # Clean excessive newlines

    return text


def create_nrc_filename(url, title, category):
    """Create good filename from URL and title (like your original!)"""

    # Use title if it's good
    if title and title != "NRC Document" and len(title) < 100:
        safe_title = re.sub(r'[^\w\s-]', '', title).strip()
        safe_title = re.sub(r'[-\s]+', '_', safe_title)
        filename = f"{safe_title.lower()}.txt"
    else:
        # Fall back to URL-based naming
        from urllib.parse import urlparse
        parsed_url = urlparse(url)
        path_parts = [p for p in parsed_url.path.split('/') if p]
        if path_parts:
            filename = '_'.join(path_parts[-2:]) + '.txt'
        else:
            filename = parsed_url.netloc.replace('.', '_') + '.txt'

    # Clean filename
    filename = re.sub(r'[^\w.-]', '_', filename)
    return filename


def create_enhanced_nrc_content(content, url, title, category):
    """Create enhanced NRC content (like your original!)"""

    # Enhanced header (matching your original!)
    header = f"""=== NUCLEAR TRAINING DOCUMENT ===
Title: {title}
Source URL: {url}
Collection Date: {datetime.now().isoformat()}
Document Type: Nuclear Regulatory/Educational Content
Document Category: {category.replace('_', ' ').title()}
Regulatory Authority: U.S. Nuclear Regulatory Commission
===================================

=== DOCUMENT CONTENT ===
{content}
"""

    return header


def create_summary():
    """Create comprehensive summary (like your original!)"""
    print("📊 Creating collection summary...")

    # Count files we collected by category
    wiki_count = 0
    nrc_count = 0
    total_size = 0
    categories_found = {}

    # Count Wikipedia files by category
    wiki_base = "data/raw/wikipedia"
    if os.path.exists(wiki_base):
        for category_folder in os.listdir(wiki_base):
            category_path = os.path.join(wiki_base, category_folder)
            if os.path.isdir(category_path):
                category_count = 0
                for filename in os.listdir(category_path):
                    if filename.endswith('.txt'):
                        wiki_count += 1
                        category_count += 1
                        filepath = os.path.join(category_path, filename)
                        total_size += os.path.getsize(filepath)

                # Also check related subfolder
                related_path = os.path.join(category_path, "related")
                if os.path.exists(related_path):
                    for filename in os.listdir(related_path):
                        if filename.endswith('.txt'):
                            wiki_count += 1
                            category_count += 1
                            filepath = os.path.join(related_path, filename)
                            total_size += os.path.getsize(filepath)

                if category_count > 0:
                    categories_found[f"Wikipedia - {category_folder}"] = category_count

    # Count NRC files by category
    nrc_base = "data/raw/nrc_documents"
    if os.path.exists(nrc_base):
        for category_folder in os.listdir(nrc_base):
            category_path = os.path.join(nrc_base, category_folder)
            if os.path.isdir(category_path):
                category_count = 0
                for filename in os.listdir(category_path):
                    if filename.endswith('.txt'):
                        nrc_count += 1
                        category_count += 1
                        filepath = os.path.join(category_path, filename)
                        total_size += os.path.getsize(filepath)

                if category_count > 0:
                    categories_found[f"NRC - {category_folder}"] = category_count

    # Convert size to MB
    total_size_mb = total_size / (1024 * 1024)

    # Create comprehensive summary

    # Save summary
    summary_file = "data/outputs/collection_summary.txt"
    os.makedirs("data/outputs", exist_ok=True)

    with open(summary_file, 'w', encoding='utf-8') as file:
        file.write(summary)

    print(f"✅ Summary saved: {summary_file}")
    print(f"📊 Collected {wiki_count + nrc_count} documents ({total_size_mb:.1f} MB)")


def collect_all_data():
    """Main function to collect all the data we need"""
    print("Starting data collection...")

    try:
        # Get Wikipedia articles
        get_wikipedia_articles()

        # Get NRC documents
        get_nrc_pages()

        # Create summary
        create_summary()

        print(" Data collection complete!")


    except Exception as error:
        print(f"❌ Data collection failed: {error}")


# If someone runs this file directly
if __name__ == "__main__":
    collect_all_data()