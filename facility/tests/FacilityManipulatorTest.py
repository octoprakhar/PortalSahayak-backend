from playwright.sync_api import sync_playwright, Page

from facility.model.ReferralDecision import ReferralDecision

from facility.constants.FacilityType import FacilityType

from facility.manipulator.FacilityManipulator import FacilityManipulator

referral_decision = ReferralDecision(disease_name="Skin Conditions", facility_type=FacilityType.BLOCK, facility_name="CHC LALBARRA (Block Level Facility)")

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=False)
    page = browser.new_page()
    page.goto("https://www.google.com")
    page.goto("https://rbsk.mohfw.gov.in/RBSK/login")
    input("Login manually and press enter....")
    manipulator = FacilityManipulator(page=page)

    manipulator.select_facility_type_and_name(referral_decision=referral_decision)
    page.wait_for_timeout(10000)