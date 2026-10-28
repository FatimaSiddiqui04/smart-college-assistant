"""
Script to generate authentic sample college documents for Smart College Assistant using fpdf2.
Generates 5 realistic PDF files matching the project report:
1. Exam_Circular_2025.pdf
2. Attendance_Policy_Rules.pdf
3. Semester_IV_ECS_Syllabus.pdf
4. Scholarship_Notice_2025.pdf
5. Academic_Calendar_2025_2026.pdf
"""

import os
from fpdf import FPDF

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_documents")
os.makedirs(OUTPUT_DIR, exist_ok=True)

class CollegePDF(FPDF):
    def __init__(self, doc_title="College Document", ref_no="ACE/2025"):
        super().__init__()
        self.doc_title = doc_title
        self.ref_no = ref_no

    def header(self):
        self.set_font('Helvetica', 'B', 13)
        self.set_text_color(26, 54, 93) # Navy blue
        self.cell(0, 7, 'ATHARVA COLLEGE OF ENGINEERING, MALAD', align='C', new_x='LMARGIN', new_y='NEXT')
        self.set_font('Helvetica', '', 9)
        self.set_text_color(74, 85, 104)
        self.cell(0, 5, 'Affiliated to University of Mumbai | Approved by AICTE & DTE | NAAC Accredited', align='C', new_x='LMARGIN', new_y='NEXT')
        self.ln(2)
        
        # Ref line
        self.set_font('Helvetica', 'B', 8)
        self.set_text_color(45, 55, 72)
        self.cell(100, 5, f'Ref No: {self.ref_no}', align='L')
        self.cell(0, 5, 'Academic Year: 2025-2026', align='R', new_x='LMARGIN', new_y='NEXT')
        
        # Horizontal rule
        self.set_draw_color(43, 108, 176)
        self.set_line_width(0.6)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(113, 128, 150)
        self.cell(0, 10, f'Atharva College of Engineering - Page {self.page_no()}', align='C')

    def add_section_title(self, title):
        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(44, 82, 130)
        self.cell(0, 7, title, new_x='LMARGIN', new_y='NEXT')
        self.ln(1)

    def add_body_paragraph(self, text):
        self.set_font('Helvetica', '', 10)
        self.set_text_color(45, 55, 72)
        self.multi_cell(0, 5.5, text)
        self.ln(2.5)

    def add_bullet(self, title, text):
        self.set_font('Helvetica', 'B', 9.5)
        self.set_text_color(26, 32, 44)
        self.cell(6, 5.5, '-', align='R')
        self.cell(4)
        self.set_font('Helvetica', 'B', 9.5)
        self.write(5.5, f"{title}: ")
        self.set_font('Helvetica', '', 9.5)
        self.set_text_color(45, 55, 72)
        self.write(5.5, f"{text}\n")
        self.ln(1.5)

# 1. Exam Circular 2025
def create_exam_circular():
    pdf = CollegePDF("Semester End Examination Guidelines", "ACE/EXAM/2025/11-04")
    
    # Page 1
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(197, 48, 48) # Dark red title
    pdf.cell(0, 8, 'CIRCULAR: SEMESTER END EXAMINATION SCHEDULE & REGULATIONS', align='C', new_x='LMARGIN', new_y='NEXT')
    pdf.ln(2)

    pdf.add_body_paragraph("To: All Students of Second Year (SE Sem-III), Third Year (TE), and Final Year (BE)\nDepartment: Electronics & Computer Science (ECS) and Allied Branches")
    pdf.add_body_paragraph("Subject: Mandatory Instructions and Submission Deadlines for Winter Session 2025 Examinations")

    pdf.add_section_title("1. General Examination Directives")
    pdf.add_body_paragraph("The Semester End Theory and Practical Examinations for all Bachelor of Engineering programs under the 2020 NEP Scheme will commence in November 2025. All eligible students must register on the university exam portal and submit physical copies of their examination application forms.")
    
    pdf.add_bullet("Theory Examination Date", "Theory Examinations for Semester III will officially commence on 24th November 2025 across designated campus examination centers.")
    pdf.add_bullet("Practical & Oral Schedule", "Practical, oral, and project evaluations will take place between 3rd November 2025 and 12th November 2025 under external university supervision.")
    pdf.add_bullet("Term Work Completion", "Students must ensure all laboratory assignments, journal logsheets, and project reports are certified and signed by course in-charges before 31st October 2025.")

    pdf.add_section_title("2. Examination Fee Structure")
    pdf.add_body_paragraph("The standard examination fees prescribed by the University of Mumbai are as follows:")
    
    # Simple table
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_fill_color(226, 232, 240)
    pdf.cell(60, 6, "Category", 1, 0, 'C', True)
    pdf.cell(45, 6, "Regular Fee", 1, 0, 'C', True)
    pdf.cell(45, 6, "Marksheet Fee", 1, 0, 'C', True)
    pdf.cell(40, 6, "Total", 1, 1, 'C', True)
    
    pdf.set_font('Helvetica', '', 9)
    pdf.cell(60, 6, "General / Open Category", 1, 0, 'L')
    pdf.cell(45, 6, "Rs. 1,450", 1, 0, 'C')
    pdf.cell(45, 6, "Rs. 100", 1, 0, 'C')
    pdf.cell(40, 6, "Rs. 1,550", 1, 1, 'C')

    pdf.cell(60, 6, "Reserved (SC/ST/OBC)", 1, 0, 'L')
    pdf.cell(45, 6, "Rs. 750", 1, 0, 'C')
    pdf.cell(45, 6, "Rs. 100", 1, 0, 'C')
    pdf.cell(40, 6, "Rs. 850", 1, 1, 'C')

    pdf.cell(60, 6, "KT / Repeater (1-2 Subjects)", 1, 0, 'L')
    pdf.cell(45, 6, "Rs. 600", 1, 0, 'C')
    pdf.cell(45, 6, "Rs. 100", 1, 0, 'C')
    pdf.cell(40, 6, "Rs. 700", 1, 1, 'C')
    pdf.ln(4)

    # Page 2 (Contains exact target sentence from report page 25/28!)
    pdf.add_page()
    pdf.add_section_title("3. Form Submission Deadlines (Mandatory Notice)")
    pdf.add_body_paragraph("According to the circular, the last date for submitting the exam form is 15 November 2025 (without late fee). Students must ensure that all course codes for core subjects and electives are accurately verified before submitting the physical copy.")
    
    pdf.add_bullet("Late Submission Penalty", "Examination forms submitted after 15th November 2025 will be accepted with a late fee penalty of Rs. 500 per candidate up until 20th November 2025.")
    pdf.add_bullet("Strict Portal Closure", "No examination applications will be entertained or accepted through any channel after 20th November 2025 at 5:00 PM under any circumstances.")

    pdf.add_section_title("4. Hall Ticket Issuance and Exam Hall Protocol")
    pdf.add_body_paragraph("Hall tickets will be made accessible on the student ERP portal from 22nd November 2025 onwards. Only students who have cleared all college tuition fees, completed term work submissions, and satisfied the attendance threshold will have their hall tickets activated.")
    
    pdf.add_bullet("Verification Protocol", "Students must print the hall ticket on A4 paper and carry both their hall ticket and college student identity card to each examination session.")
    pdf.add_bullet("Prohibited Items", "Smartphones, programmable scientific calculators, smartwatches, and notes are strictly barred inside the examination blocks. Any violation will be dealt with under Mumbai University unfair means ordinances.")

    pdf.ln(12)
    pdf.set_font('Helvetica', 'B', 9)
    pdf.cell(100, 5, "Dr. Tejaswini Jadhav", 0, 0, 'L')
    pdf.cell(0, 5, "Dr. Ramesh Kulkarni", 0, 1, 'R')
    pdf.set_font('Helvetica', '', 8.5)
    pdf.cell(100, 5, "Controller of Examinations", 0, 0, 'L')
    pdf.cell(0, 5, "Principal, Atharva College of Engineering", 0, 1, 'R')

    out_path = os.path.join(OUTPUT_DIR, "Exam_Circular_2025.pdf")
    pdf.output(out_path)

# 2. Attendance Policy Rules
def create_attendance_policy():
    pdf = CollegePDF("Attendance Policy & Norms", "ACE/ACAD/ATT/2025")
    
    # Page 1
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(197, 48, 48)
    pdf.cell(0, 8, 'ACADEMIC REGULATIONS: ATTENDANCE NORMS & ELIGIBILITY', align='C', new_x='LMARGIN', new_y='NEXT')
    pdf.ln(2)

    pdf.add_section_title("1. Minimum Attendance Requirement for Appearing in Examinations")
    pdf.add_body_paragraph("As laid down under University of Mumbai Ordinance 6086 and NEP 2020 guidelines, regular attendance across all scheduled academic components is strictly compulsory.")
    pdf.add_body_paragraph("What is the minimum attendance required to appear for exams? Every student registered in an undergraduate engineering program is required to maintain a minimum attendance of 75% in each individual theory subject, tutorial, and laboratory practical session throughout the semester.")
    
    pdf.add_bullet("Attendance Calculation", "Attendance percentage is calculated from the date of commencement of term until the last official instructional day.")
    pdf.add_bullet("Monthly Defaulter Tracking", "Defaulter lists are compiled and displayed on departmental notice boards on the 5th day of every calendar month.")
    pdf.add_bullet("Parental Intimation", "Automated SMS alerts and formal letters are dispatched to parents/guardians when cumulative attendance drops below 75%.")

    pdf.add_section_title("2. Defaulter Categories and Warning Tiers")
    pdf.add_bullet("Category A (75% and Above)", "Satisfactory attendance status. The candidate is unconditionally eligible for term grant and all internal/external semester end examinations.")
    pdf.add_bullet("Category B (60% to 74%)", "Caution status / First warning. Student along with parents must attend an academic counseling session with the class advisor and HOD.")
    pdf.add_bullet("Category C (Below 60%)", "Critical defaulter. The candidate is in violation of Mumbai University rules and is liable to be debarred from writing exams.")

    # Page 2
    pdf.add_page()
    pdf.add_section_title("3. Condonation of Attendance on Medical and Special Grounds")
    pdf.add_body_paragraph("Under exceptional situations where a student's attendance falls between 60% and 74%, condonation of attendance shortage up to a maximum of 15% may be granted by the College Academic Committee subject to:")
    
    pdf.add_bullet("Medical Illness Condonation", "Genuine hospitalization or severe illness verified by an authentic medical certificate signed by a registered medical practitioner (MBBS minimum) submitted within 7 working days of recovery.")
    pdf.add_bullet("Institutional Representation", "Prior written sanction from the Principal for representing Atharva College of Engineering or the University of Mumbai in recognized sports tournaments, technical hackathons, or youth festivals.")

    pdf.add_section_title("4. Debarment and Academic Consequences")
    pdf.add_body_paragraph("Students whose final attendance remains strictly below 75% without authorized condonation will be officially debarred from taking the semester end theory and practical examinations.")
    pdf.add_body_paragraph("A debarred student will not receive term grant for the respective semester and will be required to re-register as a repeater student during the following academic year, fulfilling all laboratory and lecture obligations anew.")

    pdf.ln(12)
    pdf.set_font('Helvetica', 'B', 9)
    pdf.cell(100, 5, "Dr. Tejaswini Jadhav", 0, 0, 'L')
    pdf.cell(0, 5, "Dr. Ramesh Kulkarni", 0, 1, 'R')
    pdf.set_font('Helvetica', '', 8.5)
    pdf.cell(100, 5, "Head of Department, ECS", 0, 0, 'L')
    pdf.cell(0, 5, "Principal, Atharva College of Engineering", 0, 1, 'R')

    out_path = os.path.join(OUTPUT_DIR, "Attendance_Policy_Rules.pdf")
    pdf.output(out_path)

# 3. Semester IV ECS Syllabus
def create_syllabus_doc():
    pdf = CollegePDF("Semester IV Syllabus Curriculum", "ACE/SYLLABUS/ECS-S4")
    
    # Page 1
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(43, 108, 176)
    pdf.cell(0, 8, 'CURRICULUM SCHEME & SYLLABUS: SE SEMESTER IV', align='C', new_x='LMARGIN', new_y='NEXT')
    pdf.ln(2)

    pdf.add_section_title("1. Course Structure and Subjects Covered in Semester IV")
    pdf.add_body_paragraph("Which subjects are covered in the Semester IV syllabus? Under the University of Mumbai NEP 2020 Scheme, the subjects covered in the Semester IV syllabus for Second Year Electronics & Computer Science (ECS) are as follows:")

    # Table
    pdf.set_font('Helvetica', 'B', 8.5)
    pdf.set_fill_color(226, 232, 240)
    pdf.cell(25, 6, "Code", 1, 0, 'C', True)
    pdf.cell(90, 6, "Subject / Course Name", 1, 0, 'L', True)
    pdf.cell(45, 6, "Scheme (L+P+T)", 1, 0, 'C', True)
    pdf.cell(30, 6, "Credits", 1, 1, 'C', True)

    courses = [
        ("ECC401", "Applied Mathematics IV (Calculus & Transforms)", "3L + 1T", "4"),
        ("ECC402", "Microcontroller Applications & Embedded Systems", "3L + 2P", "4"),
        ("ECC403", "Database Management Systems (DBMS)", "3L + 2P", "4"),
        ("ECC404", "Principles of Communication Engineering", "3L + 2P", "4"),
        ("ECC405", "Signals and Systems / Signal Processing", "3L + 0P", "3"),
        ("ECM401", "Mini Project 1B (Embedded Software System)", "0L + 4P", "2"),
    ]
    pdf.set_font('Helvetica', '', 8.5)
    for c, n, s, cr in courses:
        pdf.cell(25, 6, c, 1, 0, 'C')
        pdf.cell(90, 6, n, 1, 0, 'L')
        pdf.cell(45, 6, s, 1, 0, 'C')
        pdf.cell(30, 6, cr, 1, 1, 'C')

    pdf.ln(3)
    pdf.add_body_paragraph("Total semester academic credits: 21 Credits. Practical laboratory sessions are held in dedicated department labs with modern simulation and hardware kits.")

    # Page 2
    pdf.add_page()
    pdf.add_section_title("2. Detailed Module Outline for Core Subjects")
    pdf.add_bullet("Microcontroller Applications", "Instruction sets and architecture of ARM Cortex-M and 8051 controllers, timer and interrupt handling, GPIO interfacing, serial protocols (UART, SPI, I2C), PWM generation, and embedded C firmware design.")
    pdf.add_bullet("Database Management Systems (DBMS)", "Relational database concepts, ER diagrams, SQL DDL/DML, functional dependencies, normalization (1NF, 2NF, 3NF, BCNF), indexing (B-trees, hashing), transaction processing, ACID properties, concurrency control, and introductory NoSQL databases.")
    pdf.add_bullet("Signals and Systems", "Continuous and discrete-time signals, Linear Time-Invariant (LTI) systems, Fourier transform, Laplace transform, Z-transform, frequency response, and digital filter fundamentals.")

    pdf.add_section_title("3. Examination Evaluation and Credit Award Pattern")
    pdf.add_bullet("Internal Assessment (IA)", "Two internal unit tests of 20 marks each; the average score of both tests is incorporated into final grade calculation.")
    pdf.add_bullet("End Semester Examination (ESE)", "University theory paper of 80 marks with a duration of 3 hours covering all six syllabus modules.")
    pdf.add_bullet("Term Work (TW) & Oral Exam", "25 marks term work based on journal submission and mini project defense evaluated jointly by external and internal examiners.")

    out_path = os.path.join(OUTPUT_DIR, "Semester_IV_ECS_Syllabus.pdf")
    pdf.output(out_path)

# 4. Scholarship Notice 2025
def create_scholarship_notice():
    pdf = CollegePDF("Scholarship Guidelines Notice", "ACE/SCHOL/2025-26/02")
    
    # Page 1
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(43, 108, 176)
    pdf.cell(0, 8, 'SCHOLARSHIP & FINANCIAL ASSISTANCE NOTIFICATION', align='C', new_x='LMARGIN', new_y='NEXT')
    pdf.ln(2)

    pdf.add_section_title("1. Available Scholarship Schemes (AY 2025-2026)")
    pdf.add_body_paragraph("Atharva College of Engineering assists students in securing various State Government, Central Government, and Institutional financial assistance schemes:")
    
    pdf.add_bullet("Rajarshi Shahu Maharaj Scheme (EBC)", "50% tuition and exam fee concession for eligible students admitted via CAP with annual family income up to Rs. 8 Lakhs.")
    pdf.add_bullet("Social Justice Welfare Scholarships", "100% tuition and development fee reimbursement for SC/ST students, and 50% for OBC/VJNT/SBC category candidates.")
    pdf.add_bullet("Minority Scholarship Schemes", "Direct government financial allowance for Muslim, Christian, Buddhist, Sikh, Parsi, and Jain students.")

    pdf.add_section_title("2. How Can I Apply for a Scholarship? (Procedure)")
    pdf.add_body_paragraph("Students must strictly follow these five steps to apply for scholarship benefits:")
    pdf.add_bullet("Step 1: MahaDBT Registration", "Open an account on the Government of Maharashtra scholarship portal at mahadbt.maharashtra.gov.in using your Aadhaar number and OTP verification.")
    pdf.add_bullet("Step 2: Profile Completion", "Fill personal details, permanent address, caste particulars, and upload photograph and signature.")
    pdf.add_bullet("Step 3: College & Course Selection", "Select Atharva College of Engineering (Institute Code: 3203), choose Electronics & Computer Science, and input current academic year details.")
    pdf.add_bullet("Step 4: Upload Required Documents", "Scan and upload all mandatory certificates in high resolution PDF format.")
    pdf.add_bullet("Step 5: Physical Document Verification", "Take a printout of the submitted MahaDBT application form and submit the physical dossier at Counter No. 3 (Scholarship Section) in the College Admin Office.")

    # Page 2
    pdf.add_page()
    pdf.add_section_title("3. Mandatory Supporting Documents Checklist")
    pdf.add_body_paragraph("Applicants must attach self-attested photocopies of the following documents:")
    pdf.add_bullet("Income Certificate", "Original annual income certificate issued by the Competent Revenue Authority (Tahsildar) valid for financial year 2024-2025 (Income <= Rs. 8,00,000/- for EBC).")
    pdf.add_bullet("Domicile & Nationality", "Official Domicile Certificate issued by the Government of Maharashtra.")
    pdf.add_bullet("Caste & Validity Certificate", "Applicable for SC, ST, VJNT, and OBC students along with Non-Creamy Layer Certificate.")
    pdf.add_bullet("Allotment & Fee Receipts", "Original CAP allotment letter and current year college fee receipt.")
    pdf.add_bullet("Bank Account Passbook", "Copy of student's active nationalized bank savings passbook seeded with Aadhaar number.")

    pdf.add_section_title("4. Important Dates and Contact Point")
    pdf.add_body_paragraph("Online application submissions commence on 1st September 2025. The deadline for completing the online form and submitting hard-copy dossiers to Counter No. 3 is 30th November 2025.")
    pdf.add_body_paragraph("In case of discrepancies or biometric verification errors, contact the Scholarship In-charge Mr. Vinod Shinde at the Administrative Wing.")

    out_path = os.path.join(OUTPUT_DIR, "Scholarship_Notice_2025.pdf")
    pdf.output(out_path)

# 5. Academic Calendar 2025-2026
def create_academic_calendar():
    pdf = CollegePDF("Academic Calendar 2025-2026", "ACE/CAL/2025-26")
    
    # Page 1
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(43, 108, 176)
    pdf.cell(0, 8, 'ACADEMIC CALENDAR: ACADEMIC YEAR 2025-2026', align='C', new_x='LMARGIN', new_y='NEXT')
    pdf.ln(2)

    pdf.add_section_title("1. Odd Semester Schedule (Semesters III, V, VII)")
    pdf.add_body_paragraph("Comprehensive academic schedule for the Odd Semester instructional cycle:")

    # Table
    pdf.set_font('Helvetica', 'B', 8.5)
    pdf.set_fill_color(226, 232, 240)
    pdf.cell(110, 6, "Academic Event / Activity", 1, 0, 'L', True)
    pdf.cell(80, 6, "Scheduled Dates", 1, 1, 'C', True)

    events_odd = [
        ("Commencement of Academic Term (Lectures Start)", "15th July 2025"),
        ("Display of First Monthly Defaulters List", "5th August 2025"),
        ("Internal Assessment Examination 1 (IA-1)", "1st September - 5th September 2025"),
        ("Mid-Term Course Progress Review & Feedback", "15th September 2025"),
        ("Internal Assessment Examination 2 (IA-2)", "20th October - 24th October 2025"),
        ("Conclusion of Academic Term (End of Teaching)", "31st October 2025"),
        ("Practical & Oral University Examinations", "3rd November - 12th November 2025"),
        ("University Semester End Theory Exams", "24th November 2025 Onwards")
    ]
    pdf.set_font('Helvetica', '', 8.5)
    for ev, dt in events_odd:
        pdf.cell(110, 6, ev, 1, 0, 'L')
        pdf.cell(80, 6, dt, 1, 1, 'C')

    # Page 2
    pdf.add_page()
    pdf.add_section_title("2. Even Semester Schedule (Semesters IV, VI, VIII)")
    pdf.add_body_paragraph("Schedule for the upcoming Even Semester including start date, annual fests, and final examinations:")

    # Table
    pdf.set_font('Helvetica', 'B', 8.5)
    pdf.set_fill_color(226, 232, 240)
    pdf.cell(110, 6, "Academic Milestone", 1, 0, 'L', True)
    pdf.cell(80, 6, "Scheduled Dates", 1, 1, 'C', True)

    events_even = [
        ("When does the next semester begin?", "5th January 2026"),
        ("Atharva Annual Tech Fest 'Techithon'", "16th February - 18th February 2026"),
        ("Atharva Annual Sports Week 'Elysium'", "19th February - 21st February 2026"),
        ("Internal Assessment Examination 1 (Even Sem)", "2nd March - 6th March 2026"),
        ("Internal Assessment Examination 2 (Even Sem)", "13th April - 17th April 2026"),
        ("Conclusion of Even Semester Term", "24th April 2026"),
        ("Semester End University Theory Exams", "11th May - 30th May 2026"),
        ("Summer Vacation for Students", "1st June - 5th July 2026")
    ]
    pdf.set_font('Helvetica', '', 8.5)
    for ev, dt in events_even:
        pdf.cell(110, 6, ev, 1, 0, 'L')
        pdf.cell(80, 6, dt, 1, 1, 'C')

    pdf.ln(4)
    pdf.add_body_paragraph("Commencement Confirmation: As notified in the calendar, the next semester (Even Semester / Semester IV) begins on 5th January 2026. Students must attend classes punctually.")

    out_path = os.path.join(OUTPUT_DIR, "Academic_Calendar_2025_2026.pdf")
    pdf.output(out_path)

if __name__ == "__main__":
    print("Generating sample PDFs with fpdf2...")
    create_exam_circular()
    print("1. Exam_Circular_2025.pdf created.")
    create_attendance_policy()
    print("2. Attendance_Policy_Rules.pdf created.")
    create_syllabus_doc()
    print("3. Semester_IV_ECS_Syllabus.pdf created.")
    create_scholarship_notice()
    print("4. Scholarship_Notice_2025.pdf created.")
    create_academic_calendar()
    print("5. Academic_Calendar_2025_2026.pdf created.")
    print("All sample college PDFs created successfully in:", OUTPUT_DIR)
