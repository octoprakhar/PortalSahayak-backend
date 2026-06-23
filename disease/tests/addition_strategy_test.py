from playwright.sync_api import sync_playwright

from all_models.child_models import Child
from services.PageSynchronizer import PageSynchronizer
from disease.strategy.adding_strategies.checkbox_adding.SkinDiseaseAdditionStrategy import SkinDiseaseAdditionStrategy
from disease.strategy.adding_strategies.checkbox_adding.DentalDiseaseAddingStrategy import DentalDiseaseAdditionStrategy
from disease.repository.DiseaseRepository import DiseaseRepository
from disease.strategy.adding_strategies.value_adding.SevereStuntingAddingStrategy import SevereStuntingAddingStrategy
from disease.strategy.adding_strategies.value_adding.MildAnaemiaAddingStrategy import MildAnaemiaAddingStrategy
from disease.strategy.adding_strategies.value_adding.ModerateAnaemiaAddingStrategy import ModerateAnaemiaAddingStrategy


child = Child(
    name="A",
    dob="16-10-2023",
    facilityName="B",
    motherName="c",
    mobileNumber="9999999999",
    gender="Male",
    address="xyz",
    height="70.5",
    weight="5.4",
    diseaseName="",
    hb="10",
    headCircumference="47",
    fatherName="None",
    facilityType="None",
    visionLeft="6/6",
    visionRight="6/6"
)

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=False)
    page = browser.new_page()
    page.goto("https://www.google.com")
    page.goto("https://rbsk.mohfw.gov.in/RBSK/login")
    input("Login manually and press enter....")

    # skin_disease_addition_strategy = SkinDiseaseAdditionStrategy()
    # dental_disease_addition_strategy = DentalDiseaseAdditionStrategy()
    # severe_stunting_addition_strategy = SevereStuntingAddingStrategy()
    # mild_anaemia_addition_strategy = MildAnaemiaAddingStrategy()
    # moderate_anaemia_addition_strategy = ModerateAnaemiaAddingStrategy()

    page.wait_for_timeout(5000)
    # skin_disease_addition_strategy.add(child=child,page=page,synchronizer=PageSynchronizer(),repository=DiseaseRepository())
    # dental_disease_addition_strategy.add(child=child,page=page,synchronizer=PageSynchronizer(),repository=DiseaseRepository())
    # moderate_anaemia_addition_strategy.add(child=child,page=page,synchronizer=PageSynchronizer(),repository=DiseaseRepository())
    page.wait_for_timeout(5000)