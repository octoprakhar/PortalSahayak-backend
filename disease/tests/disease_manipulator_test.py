from playwright.sync_api import sync_playwright

from disease.manipulator.DiseaseManipulator import DiseaseManipulator
from disease.models.DiseaseDefinition import DiseaseDefinition,DiseaseQuestion
from disease.models.DiseaseCategory import DiseaseCategory
from services.PageSynchronizer import PageSynchronizer


detected_disease = DiseaseDefinition(name="Downs Syndrome",code="2",category=DiseaseCategory.DEFECTS_AT_BIRTH,questions=[DiseaseQuestion(code="A10",text="Features Suggestive of Down’s Syndrome (Refer Pictorial)(Refer if more than one sign is present)")])
detected_disease_2 = DiseaseDefinition(name="Vitamin A Deficiency",code="11",category=DiseaseCategory.DEFICIENCIES,questions=[DiseaseQuestion(code="B4",text="Vitamin A Deficiency: Ask for night blindness/look for Bitot’s spot.")])
with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=False)
    page = browser.new_page()
    page.goto("https://www.google.com")
    page.goto("https://rbsk.mohfw.gov.in/RBSK/login")
    input("Login manually and press enter....")
    diseaseManipulator = DiseaseManipulator(page=page,synchronizer=PageSynchronizer())
    # diseaseManipulator.click_check_box(disease=detected_disease)
    # diseaseManipulator.uncheck_box(disease=detected_disease)
    # diseaseManipulator.set_height("99.4")
    # diseaseManipulator.set_weight("16.8")
    # diseaseManipulator.set_head_circumference("52")
    diseaseManipulator.set_hb("16")
    page.wait_for_timeout(5000)