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
from disease.strategy.removal_strategies.value_removal.MicrocephelyRemovalStrategy import MicrocephelyRemovalStrategy



detected_disease = DiseaseDefinition(name="Downs Syndrome",code="2",category=DiseaseCategory.DEFECTS_AT_BIRTH,questions=[DiseaseQuestion(code="A10",text="Features Suggestive of Down’s Syndrome (Refer Pictorial)(Refer if more than one sign is present)")])
detected_disease_2 = DiseaseDefinition(name="Vitamin A Deficiency",code="11",category=DiseaseCategory.DEFICIENCIES,questions=[DiseaseQuestion(code="B4",text="Vitamin A Deficiency: Ask for night blindness/look for Bitot’s spot.")])
value_detected_disease = DiseaseDefinition(name = "Microcephaly",code="42",category=DiseaseCategory.DEFECTS_AT_BIRTH,questions=[DiseaseQuestion(code="A1", text="Head: Abnormally large or small in size/shape deformity. Size Check > 2SD < 2 D and mark")])
with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=False)
    page = browser.new_page()
    page.goto("https://www.google.com")
    page.goto("https://rbsk.mohfw.gov.in/RBSK/login")
    input("Login manually and press enter....")
    # removal_strategy_checkbox = CheckboxRemovalStrategy()
    # removal_strategy_checkbox.remove(disease=DetectedDisease(definition=detected_disease,source=DiseaseSource.UNKNOWN), page=page,synchronizer=PageSynchronizer())
    # removal_strategy = SamValueRemovalStrategy(page=page,synchronizer=PageSynchronizer())
    removal_strategy = MicrocephelyRemovalStrategy()
    removal_strategy.remove(disease=DetectedDisease(definition=value_detected_disease,source=DiseaseSource.UNKNOWN),page=page, synchronizer=PageSynchronizer())
    page.wait_for_timeout(7000)