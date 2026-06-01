from playwright.sync_api import sync_playwright

def select_disease(page,disease_name):
    tabs = [
        "Defects at Birth",
        "Deficiencies",
        "Childhood Diseases",
        "Development Delay"
    ]

    for tab in tabs:
        page.get_by_role("button", name=tab).click()

        page.wait_for_timeout(1000)

        row = page.locator("tr").filter(has_text=disease_name)

        if row.count() > 0:
            row.locator('input[type="checkbox"]').click()

            return True
        
    return False

def select_facility(page, facility_type, facility_name):

    # Step 1: click checkbox
    refer_checkbox = page.locator('#referSameInstitute')

    refer_checkbox.check()

    # Step 2: scope inside referral section
    referral_section = page.locator("div").filter(
        has_text="Refer to same facility for all Health Conditions"
    )

    # Step 3: facility type dropdown
    facility_type_input = referral_section.locator(
        'input[role="combobox"]'
    ).first

    facility_type_input.click()

    facility_type_input.fill(facility_type)

    page.get_by_role(
        "option",
        name=facility_type
    ).click()

    # Step 4: facility name dropdown
    facility_name_input = referral_section.locator(
        'input[role="combobox"]'
    ).nth(1)

    facility_name_input.click()

    facility_name_input.fill(facility_name)

    page.get_by_role(
        "option",
        name=facility_name
    ).click()

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=False)
    page = browser.new_page()
    page.goto("https://www.google.com")
    page.goto("https://rbsk.mohfw.gov.in/RBSK/login")
    input("Login manually and press enter....")
    page.locator('[title="Screening"]').click()
    page.wait_for_timeout(5000)
    page.locator('[name="financialMonth"]').select_option(label="May 2026")
    page.get_by_role('button',name='Search').click()
    page.wait_for_load_state('networkidle')
    page.wait_for_timeout(5000)
    input("Select the institution you want to fill students and then click enter....")
    
    #Adding new child now
    page.get_by_role('button',name="Add New Child").click()
    page.wait_for_timeout(1000)
    page.get_by_role('button',name="Proceed").click()
    childNameField = page.locator('[name="studentName"]').fill("KUSHAGRA")
    dobField = page.locator('[placeholder="dd-mm-yyyy"]')
    genderDropDown = page.locator('[name="gender"]')
    motherNameField = page.locator('[name="motherName"]')
    fatherNameField = page.locator('[name="fatherName"]')
    mobileNumberField = page.locator('[name="mobile"]')
    addressField = page.locator('[name="address"]')
    ageField = page.locator('[name="age"]')
    


    dobField.fill("27-07-2025")
    genderDropDown.select_option(label="Male")
    motherNameField.fill("SARITA")
    fatherNameField.fill("LAXMICHAND")
    mobileNumberField.fill("8770928336")
    addressField.fill("Kanki")

    if float(ageField.input_value()) < 1:
        birthWeightField = page.locator('[name="birthWeight"]')
        birthWeightField.fill("2500")
    

    input("Please press enter to move forward....")

    saveChildBtn = page.get_by_role('button',name='Save & Start Screening')
    saveChildBtn.click()

    # Child's health report
    heightField = page.locator('[name="height"]')
    weightField = page.locator('[name="weight"]')
    headCircumField = page.locator('[name="headCircumference"]')
    hbField = page.locator('[name="hb"]')
    muacFIeld = page.locator('[name="muac"]')

    heightField.fill("66")
    weightField.fill("6.6")
    headCircumField.fill("43")
    hbField.fill("9")
    muacFIeld.fill("13")

    ## Any disease selection
    disease_name = "Skin Conditions"
    select_disease(page,disease_name=disease_name)

    ## Select facility only when visible, it could not be visible if child is healthy
    referral_checkbox = page.locator('#referSameInstitute')

    if referral_checkbox.is_visible():
        select_facility(page,"Block Level Facility","CHC LALBARRA (Block Level Facility)")

    finalSubmitBtn = page.get_by_role('button',name='Preview & Submit')
    page.wait_for_timeout(5000)
    finalSubmitBtn.click()

    input("Press enter to close")
    print(page.title())
    browser.close()

# LALBARRA-R1
# Trapti@1234