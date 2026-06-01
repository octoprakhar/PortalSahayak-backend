## THis class will just load the data from various sources, and validate it, for now or sometimes it is also may work with transformation, or 
## Maybe shilfted to future thing.

import pandas as pd
import logging
import re


from all_models.child_models import Child 
from services.ChildDataValidation import ChildDataValidation
from services.SamClassifier import SAMClassifier
from utils.loaderUtils import get_age,get_head_circumference, clean_dob, normalize_hb,normalize_gender,fill_disease_from_nan, standardize_facility


class ChildLoader:


    def loadViaExcel(self, url):

        try:
            df = pd.read_excel(url)
            logging.info(f"Loaded data via excel with shape: {df.shape}")
            return df

        except Exception as e:
            logging.error(f"Failed to load excel: {e}")
            raise

    
    def loadViaCsv(self,url) -> pd.DataFrame:
        ## Maybe changing it to dataframe
        try:
            df = pd.read_csv(url)
            shape = df.shape
            logging.info(
                f"Dataframe loaded with csv and shape: {shape}"
            )
            return df
        except Exception as e:
            logging.error(f"Failed to load csv: {e}")
            raise
    
    
    def clean_column_name(self,col:str):

        # Just remove leading and trailing space
        col = col.strip()

        # if column name is something like 'unnamed' remove it
        if col.lower().startswith('unnamed'):
            return None
    
        ## If column name is already written in correct form then just leave it
        if re.match(r'^[a-z]+([A-Z][a-z0-9]*)*$', col):
            return col
    
        # Removing special characters with a space
        col = re.sub(r'[_\-\s]+', ' ', col)

        ## Making camel case
        words = col.split()

        return words[0].lower() + ''.join(word.capitalize() for word in words[1:])        

    def clean_df(self,df:pd.DataFrame,defaultContactNum:str, address:str)-> pd.DataFrame:
        cleaned_df = df.copy()

        ## Lets I begin with steps:
        ## Step 1: Generic cleaning of column names
        cleaned_columns = [self.clean_column_name(col) for col in cleaned_df.columns]
        cleaned_df = cleaned_df.loc[:, [c is not None for c in cleaned_columns]]
        cleaned_df.columns = [c for c in cleaned_columns if c is not None]
        logging.info(f"Columns got generic cleaned and names are : {str(cleaned_df.columns)}")

        cleaned_df["hb"] = cleaned_df["hb"].apply(normalize_hb)
        logging.info(f"hb got normalized")

        cleaned_df["gender"] = cleaned_df["gender"].apply(normalize_gender)
        logging.info("Gender got normalized to Male and Female")

        cleaned_df["diseaseName"] = cleaned_df["diseaseName"].astype(str)
        cleaned_df['mobileNumber'] = cleaned_df["mobileNumber"].fillna(defaultContactNum).astype(str) 
        cleaned_df['visionLeft'] = cleaned_df["visionLeft"].fillna("6/6").astype(str)
        cleaned_df['visionRight'] = cleaned_df["visionRight"].fillna("6/6").astype(str)
        cleaned_df['facilityType'] = cleaned_df["facilityType"].fillna("").astype(str)
        cleaned_df['facilityName'] = cleaned_df["facilityName"].fillna("").astype(str)

        cleaned_df['address'] = cleaned_df["address"].fillna(address).astype(str)
        

        

        return cleaned_df
    
    def transform_df(self,df:pd.DataFrame)-> pd.DataFrame:
        trans_df = df.copy()
        ## Let's see which column we need for transformation
        ## 1. headCircumference : filling null value wrt age as 
        ### 0-1 : 43, 1-2: 46, 2-3: 48, 3+: 50
        mask = trans_df["headCircumference"].isna()
        trans_df.loc[mask,"headCircumference"] = (
        trans_df.loc[mask,'dob']
        .apply(get_age)
        .apply(get_head_circumference)
        )
        logging.info("Filled missing value of head circumference")

        ## 2. DOB: changing all formats of dob to dd-mm-yyyy and string
        trans_df['dob'] = trans_df['dob'].apply(clean_dob)
        logging.info("DOB got transformed.")

        ## 3. Filling randomly 15% of students with NaN diseaseName either skin or dental with 3:1 ratio
        trans_df = fill_disease_from_nan(trans_df)
        logging.info("Random diseases got set")

        ## Mapping faculty name with DEIC, NRC, CHC(default)
        samClassifier = SAMClassifier()
        trans_df = standardize_facility(trans_df,samClassifier,1)
        logging.info("Facilities got mapped wrt facility Name")
        logging.info(
    f"💣💣 Got number of SAM students as {trans_df[trans_df['facilityType']=='NRC'].shape[0]}"
)

        return trans_df
    

    
    def loadData(self,url,defaultContactNum:str,address:str)-> list[Child]:
        ## Load it
        logging.info("🧐 Data started loading")
        df = self.loadViaCsv(url)

        logging.info("-----------Data cleaning started-------------------")
        cleaned_df = self.clean_df(df,defaultContactNum,address=address)
        logging.info("🎉🎉 Cleaning process ends here. Transformation is starting....")
        
        logging.info("-----------------------Data Transformation started-----------------------------")
        trans_df = self.transform_df(cleaned_df)
        logging.info("🎉🎉 Transformation process ends here. Transformation is starting....")
#         logging.info("=================================Data after Transformation==================================")
#         logging.info(
#     "\n" +
#     str(
#         trans_df[['name', 'facilityType', 'facilityName']]
#         .head(20)
#     )
# )
        
        logging.info("---------------------------Data Validation started--------------------------------")
        childDataValidation = ChildDataValidation()
        valid_df, invalid_df = childDataValidation.validate_df(trans_df)
        logging.info(f"🎉🎉🎉 Data validation completed, got valid data with shape {valid_df.shape} and invalid data with shape {invalid_df.shape}")
#         logging.info("=================================Data after Validation==================================")
#         logging.info(
#     "\n" +
#     str(
#         valid_df[['name', 'facilityType', 'facilityName']]
#         .head(20)
#     )
# )
        
        
        invalid_df.to_excel("invalid_student_data.xlsx",index=False)

        children = []

        for _, row in valid_df.iterrows():
            
            child = Child(
                name=str(row["name"]),
                dob=str(row["dob"]),
                fatherName=str(row["fatherName"]),
                motherName=str(row["motherName"]),
                mobileNumber=str(row["mobileNumber"]),
                gender=str(row["gender"]),
                address=str(row["address"]),
                height=str(row["height"]),
                weight=str(row["weight"]),
                diseaseName=str(row.get("diseaseName")),
                hb=str(row.get("hb")),
                headCircumference=str(row.get("headCircumference")),
                facilityType=str(row.get("facilityType")),
                facilityName=str(row.get("facilityName")),
            )
            # logging.info(f"Created child like: {str(child)}")
#             logging.info(
#     f"CHILD => "
#     f"Name={child.name} | "
#     f"FacilityType={child.facilityType} | "
#     f"FacilityName={child.facilityName}"
# )

            children.append(child)

        return children



