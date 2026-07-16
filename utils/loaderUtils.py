import numpy as np
import pandas as pd
import re
import datetime
import logging
import random


def get_age(dob):
    """
    Returns age in years from dob.
    Accepts string, datetime, Timestamp, or None.
    """
    if pd.isna(dob):
        return None
    
    # Convert to string and remove spaces
    dob_str = str(dob).strip()

    # Require day/month/year
    pattern = r'^\d{1,2}[/-]\d{1,2}[/-]\d{2,4}$'

    if not re.match(pattern, dob_str):
        return None
    
    ## Now let's convert it safely
    dob = pd.to_datetime(
        dob,
        dayfirst=True,
        errors='coerce'
    )

    ## If invalid date
    if pd.isna(dob):
        return None
    
    ## Calculating age
    today = pd.Timestamp.today()

    return (today-dob).days / 365.25


def get_head_circumference(age):
    """
    Returns head circumference of the child if age is given
    """
    if pd.isna(age):
        return None
    
    if age < 1:
        return 43
    elif age < 2:
        return 46
    elif age < 3:
        return 48
    else:
        return 50



def clean_dob(dob):
    """
    For any format of DOB , it changes to dd-mm-yyyy, and string
    """

    if pd.isna(dob):
        return pd.NA
    
    dob_str = str(dob).strip()

    # Require day-month-year structure
    pattern = r'^\d{1,2}[/-]\d{1,2}[/-]\d{2,4}$'

    if not re.match(pattern, dob_str):
        return pd.NA
    
    ## Convert it safely
    dob = pd.to_datetime(
        dob_str,
        dayfirst=True,
        errors='coerce'
    )

    if pd.isna(dob):
        return pd.NA
    
    return dob.strftime('%d-%m-%Y')

def normalize_hb(hb):
    """
    Checks hb value:
    - If missing or invalid, assigns a random value between 11.0 and 14.0 (1 decimal place).
    - If valid and exceeds 14, caps it at 14.0.
    """
    # Check if the value is missing, null, or not a number
    if pd.isna(hb) or (not isinstance(hb, (int, float))):
        # Generate a random float between 11.0 and 14.0 and round to 1 decimal place
        return round(random.uniform(12.0, 14.0), 1)
    
    # Cap values exceeding 14
    if hb > 14:
        return 14.0
        
    return hb

import pandas as pd

def normalize_gender(gender: str):
    # Check if the value is missing or not a string
    if pd.isna(gender) or not isinstance(gender, str):
        return pd.NA
    
    # Clean up whitespace and convert to lowercase once
    clean_gender = gender.strip().lower()
    
    if clean_gender in ["male", "m"]:
        return "Male"
    elif clean_gender in ["female", "f"]:
        return "Female"
    else:
        return pd.NA


def fill_disease_from_nan(df:pd.DataFrame, column='diseaseName', ratio=0.15, seed=42):

    """
    Filling randomly 15% of students with NaN diseaseName either skin or dental with 3:1 ratio
    """

    np.random.seed(seed)

    # Step 1: only NaN rows
    nan_indices = df[df[column].isna()].index

    # Step 2: pick 15% of NaNs
    n = int(ratio * len(nan_indices))

    if n == 0:
        return df  # nothing to fill

    selected = np.random.choice(nan_indices, size=n, replace=False)

    # Step 3: split 3:1
    skin_count = int(0.75 * n)

    skin_idx = selected[:skin_count]
    dental_idx = selected[skin_count:]

    # Step 4: fill
    df.loc[skin_idx, column] = 'Skin Conditions'
    df.loc[dental_idx, column] = 'Dental Conditions'

    return df

def get_corrected_values(age_years):
    """
    Returns corrected weight and height
    according to age group.
    """

    if age_years < 1:
        return (
            round(random.uniform(6, 8), 1),
            round(random.uniform(60, 70), 1)
        )

    elif age_years < 2:
        return (
            round(random.uniform(9, 11), 1),
            round(random.uniform(70, 80), 1)
        )

    elif age_years < 3:
        return (
            round(random.uniform(9, 11), 1),
            round(random.uniform(80, 90), 1)
        )

    elif age_years < 4:
        return (
            round(random.uniform(12, 14), 1),
            round(random.uniform(90, 100), 1)
        )

    elif age_years < 5:
        return (
            round(random.uniform(13, 15), 1),
            round(random.uniform(95, 105), 1)
        )

    elif age_years < 6:
        return (
            round(random.uniform(14, 16), 1),
            round(random.uniform(100, 110), 1)
        )
    
    elif age_years < 7:
        return (
            round(random.uniform(17, 21), 1),
            round(random.uniform(110, 125), 1)
        )
    
    elif age_years < 8:
        return (
            round(random.uniform(22,30), 1),
            round(random.uniform(125, 135), 1)
        )
    
    elif age_years < 9:
        return (
            round(random.uniform(30, 40), 1),
            round(random.uniform(140, 150), 1)
        )
    
    elif age_years < 10:
        return (
            round(random.uniform(35,40), 1),
            round(random.uniform(140, 150), 1)
        )
    
    elif age_years < 11:
        return (
            round(random.uniform(35, 40), 1),
            round(random.uniform(140, 150), 1)
        )
    
    elif age_years < 12:
        return (
            round(random.uniform(35, 40), 1),
            round(random.uniform(140, 150), 1)
        )
    
    elif age_years < 13: 
        return (
            round(random.uniform(35, 45), 1),
            round(random.uniform(145, 155), 1)
        )
    
    elif age_years < 14:
        return (
            round(random.uniform(35, 50), 1),
            round(random.uniform(145, 160), 1)
        )
    
    elif age_years < 15:
        return (
            round(random.uniform(45, 55), 1),
            round(random.uniform(155, 165), 1)
        )
    
    elif age_years < 16:
        return (
            round(random.uniform(45, 55), 1),
            round(random.uniform(155, 165), 1)
        )
    
    elif age_years < 17:
        return (
            round(random.uniform(45, 60), 1),
            round(random.uniform(155, 170), 1)
        )
    
    elif age_years < 18:
        return (
            round(random.uniform(50, 60), 1),
            round(random.uniform(160, 170), 1)
        )
    
    else:
        return (
            round(random.uniform(50, 60), 1),
            round(random.uniform(160, 170), 1)
        )





def standardize_facility(df):

    for idx, row in df.iterrows():

        # --------------------------------
        # SKIP INVALID DOB
        # --------------------------------

        if pd.isna(row['dob']):
            continue

        facility = str(row['facilityName']).strip().lower()


        # --------------------------------
        # FACILITY TYPES TO HANDLE
        # --------------------------------

        valid_facility = (
            facility == ''
            or facility == 'nan'
            or 'chc' in facility
            or 'nrc' in facility
        )

        # --------------------------------
        # EMPTY / CHC / NRC
        # --------------------------------

        if valid_facility:

            df.loc[idx, 'facilityType'] = (
                'Block Level Facility'
            )

            df.loc[idx, 'facilityName'] = (
                'CHC LALBARRA (Block Level Facility)'
            )

        # --------------------------------
        # DEIC CONDITION
        # --------------------------------

        elif 'deic' in facility:

            df.loc[idx, 'facilityType'] = 'DEIC'

            df.loc[idx, 'facilityName'] = (
                'DEIC Balaghat (DEIC)'
            )

        # --------------------------------
        # NORMAL CHILDREN
        # --------------------------------

        else:

            df.loc[idx, 'facilityType'] = (
                'Block Level Facility'
            )

            df.loc[idx, 'facilityName'] = (
                'CHC LALBARRA (Block Level Facility)'
            )

    return df


def standardize_height_weight(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    ages = df["dob"].apply(get_age)

    corrected = ages.apply(
        lambda age: get_corrected_values(age)
        if pd.notna(age)
        else (None, None)
    )

    df["_corrected_weight"] = corrected.apply(lambda x: x[0])
    df["_corrected_height"] = corrected.apply(lambda x: x[1])

    weight_mask = df["weight"].isna()
    height_mask = df["height"].isna()

    df.loc[weight_mask, "weight"] = df.loc[weight_mask, "_corrected_weight"]
    df.loc[height_mask, "height"] = df.loc[height_mask, "_corrected_height"]

    df.drop(columns=["_corrected_weight", "_corrected_height"], inplace=True)

    return df