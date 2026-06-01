import os
import pandas as pd
from datetime import datetime

class SAMClassifier:
    def __init__(self):

        base_dir = os.path.dirname(__file__)  # folder of SamClassifier.py

        who_dir = os.path.join(base_dir, "WHO_data")

        self.tables = {

            ("male", "wfl"):
                pd.read_excel(

                    os.path.join(
                        who_dir,
                        "wfl_boys_0-to-2-years_zscores.xlsx"
                    )
                ),

            ("female", "wfl"):
                pd.read_excel(
                    os.path.join(
                        who_dir,
                        "wfl_girls_0-to-2-years_zscores.xlsx"
                    )
                ),

            ("male", "wfh"):
                pd.read_excel(
                    os.path.join(
                        who_dir,
                        "wfh_boys_2-to-5-years_zscores.xlsx"
                    )
                ),

            ("female", "wfh"):
                pd.read_excel(
                    os.path.join(
                        who_dir,
                        "wfh_girls_2-to-5-years_zscores.xlsx"
                    )
                )
        }

    def age_months(self,dob:str):
        """
        It converts age in months. And dob must be in 
        string and format dd-mm-yyyy
        """

        if pd.isna(dob):
            return None
    
        dob = datetime.strptime(dob,"%d-%m-%Y")
        days = (datetime.today() - dob).days

        return days / 30.4375
    
    def get_table(self,sex:str,age_months):
        sex = sex.lower()

        if age_months < 24:
            return self.tables[(sex,"wfl")]
        
        return self.tables[(sex, "wfh")]
    
    def get_measurement_column(self,df:pd.DataFrame):
        """
        It will return which column actually the table has
        like either it has 'Height' or 'Length'
        """

        if "Length" in df.columns:
            return "Length"
        if "Height" in df.columns:
            return "Height"
        
        raise Exception("No Length/height column found")
    
    def nearest_row(self, df:pd.DataFrame, measurement_col:str, value):
        """
        It gives the nearest row after substracting value from each measurement col
        so nearest wins. We will get the row from which we will need to calculate the weight.
        """
        idx = (
            df[measurement_col] - value
        ).abs().idxmin()

        return df.loc[idx]
    
    def classify(self, dob, sex, weight, height):

        if pd.isna(dob):
            return None

        age = self.age_months(dob)

        df = self.get_table(sex, age)

        measurement_col = self.get_measurement_column(df)

        row = self.nearest_row(
            df,
            measurement_col,
            height
        )

        minus3sd = row["SD3neg"]
        minus2sd = row["SD2neg"]
        minus1sd = row["SD1neg"]

        # --------------------------------

        if weight < minus2sd:

            status = "SAM"
            message = "Severe Acute Malnutrition"

        elif weight < minus1sd:

            status = "MAM"
            message = "Moderate Acute Malnutrition"

        else:

            status = "Normal"
            message = "No acute malnutrition"

        return {

            "age_months": round(age, 1),

            "used_standard":
                "WFL" if age < 24 else "WFH",

            "minus3sd_cutoff":
                minus3sd,

            "minus2sd_cutoff":
                minus2sd,

            "status":
                status,

            "message":
                message
        }