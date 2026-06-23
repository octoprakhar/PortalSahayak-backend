from playwright.sync_api import sync_playwright

from disease.detector.DiseaseDetector import DiseaseDetector


with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=False)
    page = browser.new_page()
    page.goto("https://www.google.com")
    page.goto("https://rbsk.mohfw.gov.in/RBSK/login")
    input("Login manually and press enter....")
    diseaseDetector = DiseaseDetector(page=page)
    all_diseases = diseaseDetector.detect()

    if not all_diseases:
        print("No disease found")

    for disease in all_diseases:
        print(disease)
        print("===============================")
