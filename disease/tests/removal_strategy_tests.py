from playwright.sync_api import sync_playwright

from disease.manipulator.DiseaseManipulator import DiseaseManipulator
from disease.models.DiseaseDefinition import DiseaseDefinition,DiseaseQuestion
from disease.strategy.removal_strategies.checkbox_removal.CheckBoxRemovalStrategy import CheckboxRemovalStrategy
from disease.strategy.removal_strategies.DiseaseRemovalStrategy import DiseaseRemovalStrategy
from disease.models.DiseaseCategory import DiseaseCategory
from services.PageSynchronizer import PageSynchronizer
from disease.models.DetectedDisease import DetectedDisease
from disease.models.DiseaseSource import DiseaseSource

from disease.strategy.removal_strategies.value_removal.SamValueRemovalStrategy import SamValueRemovalStrategy



detected_disease = DiseaseDefinition(name="Downs Syndrome",code="2",category=DiseaseCategory.DEFECTS_AT_BIRTH,questions=[DiseaseQuestion(code="A10",text="Features Suggestive of Down’s Syndrome (Refer Pictorial)(Refer if more than one sign is present)")])
detected_disease_2 = DiseaseDefinition(name="Vitamin A Deficiency",code="11",category=DiseaseCategory.DEFICIENCIES,questions=[DiseaseQuestion(code="B4",text="Vitamin A Deficiency: Ask for night blindness/look for Bitot’s spot.")])
value_detected_disease = DiseaseDefinition(name = "SAM/Severe Thinness/SUW",code="13",category=DiseaseCategory.DEFICIENCIES,questions=[DiseaseQuestion(code="B1", text="SAM: Weight for Height/length: refer if the child is less than- 3 SD as per WHO chart, counsel if <-2 SD.lf age< 6 months use Wt/for age and >60 months use BMl"),DiseaseQuestion(code="B2",text="SAM- Oedema: Bilateral pitting oedema . Child may have skin lesions or thinning hair.")])
with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=False)
    page = browser.new_page()
    page.goto("https://www.google.com")
    page.goto("https://rbsk.mohfw.gov.in/RBSK/login")
    input("Login manually and press enter....")
    # removal_strategy_checkbox = CheckboxRemovalStrategy()
    # removal_strategy_checkbox.remove(disease=DetectedDisease(definition=detected_disease,source=DiseaseSource.UNKNOWN), page=page,synchronizer=PageSynchronizer())
    sam_removal_strategy = SamValueRemovalStrategy(page=page,synchronizer=PageSynchronizer())
    sam_removal_strategy.remove(disease=DetectedDisease(definition=value_detected_disease,source=DiseaseSource.UNKNOWN))
    page.wait_for_timeout(7000)