import pandas as pd
import numbers


class ChildDataValidation:

    """
        Validate each column one by one, if any row doesn't pass validation put it in invalid_row df, with adding another column as "error" and write the reason
        and then finally return the valid row as df, and also save invalid_row as csv, or excel.

    """

    def _is_empty(self, value):

        if pd.isna(value):
            return True

        if isinstance(value, str) and not value.strip():
            return True

        return False
    
    def _validate_string_column(
        self,
        df: pd.DataFrame,
        column_name: str
    ) -> tuple[pd.DataFrame, pd.DataFrame]:

        valid_rows = []
        invalid_rows = []

        for _, row in df.iterrows():

            value = row[column_name]

            error = None

            if self._is_empty(value):
                error = f"{column_name} is empty"

            elif not isinstance(value, str):
                error = f"{column_name} is not a string"

            if error:

                invalid_row = row.copy()
                invalid_row["error"] = error

                invalid_rows.append(invalid_row)

            else:
                valid_rows.append(row)

        return (
            pd.DataFrame(valid_rows),
            pd.DataFrame(invalid_rows)
        )
    
    def _validate_float_column(
        self,
        df: pd.DataFrame,
        column_name: str
    ) -> tuple[pd.DataFrame, pd.DataFrame]:

        valid_rows = []
        invalid_rows = []

        for _, row in df.iterrows():

            value = row[column_name]

            error = None

            if self._is_empty(value):
                error = f"{column_name} is empty"

            elif not isinstance(value, numbers.Number):
                error = f"{column_name} is not numeric"

            if error:

                invalid_row = row.copy()
                invalid_row["error"] = error

                invalid_rows.append(invalid_row)

            else:
                valid_rows.append(row)

        return (
            pd.DataFrame(valid_rows),
            pd.DataFrame(invalid_rows)
        )
    
    def validate_name(self,df:pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Validate the name of all rows of dataframe
        """
        return self._validate_string_column(df, "name")
    

    def validate_father_mother_name(self,df:pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Validate the name of child's father and mother. 
        """
        valid_rows = []
        invalid_rows = []

        for _, row in df.iterrows():

            errors = []

            father_name = row["fatherName"]
            mother_name = row["motherName"]

            if self._is_empty(father_name):
                errors.append("fatherName is empty")

            elif not isinstance(father_name, str):
                errors.append("fatherName is not string")

            if self._is_empty(mother_name):
                errors.append("motherName is empty")

            elif not isinstance(mother_name, str):
                errors.append("motherName is not string")

            if errors:

                invalid_row = row.copy()
                invalid_row["error"] = ", ".join(errors)

                invalid_rows.append(invalid_row)

            else:
                valid_rows.append(row)

        return (
            pd.DataFrame(valid_rows),
            pd.DataFrame(invalid_rows)
        )

    def validate_dob(self,df:pd.DataFrame) -> tuple[pd.DataFrame,pd.DataFrame]:
        """
        Transformation has already transformed dob in string and dd-mm-yyyy format, so just check if any row has NaN or empty rows
        """

        return self._validate_string_column(df, "dob")

    def validate_gender(self,df:pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        If gender column is empty or NaN it will invalidate
        """
        return self._validate_string_column(df, "gender")

    def validate_address(self,df:pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        If address column is empty or NaN it will invalidate
        """
        return self._validate_string_column(df, "address")

    def validate_height(self,df:pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        If height column is empty or NaN it will invalidate, and also validate that it is float.
        """
        return self._validate_float_column(df, "height")

    def validate_weight(self,df:pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        If weight column is empty or NaN it will invalidate, and also validate that it is float.
        """
        return self._validate_float_column(df, "weight")

    def validate_hb(self,df:pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        If hb column is empty or NaN it will invalidate, and also validate that it is float.
        """
        return self._validate_float_column(df, "hb")

    def validate_head_circumference(self,df:pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        If head circumference column is empty or NaN it will invalidate, and also validate that it is float.
        """
        return self._validate_float_column(
            df,
            "headCircumference"
        )

    def validate_vision_data(self,df:pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        If visionLeft, and visionRight column is empty or NaN it will invalidate, and also validate that it is str = '6/6'.
        """
        valid_rows = []
        invalid_rows = []

        for _, row in df.iterrows():

            errors = []

            for column in ["visionLeft", "visionRight"]:

                value = row[column]

                if self._is_empty(value):
                    errors.append(f"{column} is empty")

                elif not isinstance(value, str):
                    errors.append(f"{column} is not string")

                elif "/" not in value:
                    errors.append(f"{column} format invalid")

            if errors:

                invalid_row = row.copy()
                invalid_row["error"] = ", ".join(errors)

                invalid_rows.append(invalid_row)

            else:
                valid_rows.append(row)

        return (
            pd.DataFrame(valid_rows),
            pd.DataFrame(invalid_rows)
        )




    def validate_df(self, df:pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:

        required_columns = ['name', 'dob', 'fatherName', 'motherName', 'mobileNumber', 'gender',
       'address', 'height', 'weight', 'diseaseName', 'hb', 'headCircumference',
       'facilityType', 'facilityName', 'visionLeft', 'visionRight']
        
        missing_columns = set(required_columns) - set(df.columns)

        if missing_columns:
            raise ValueError(
                f"Missing columns: {missing_columns}"
            )

        validators = [
            self.validate_name,
            self.validate_father_mother_name,
            self.validate_dob,
            self.validate_gender,
            self.validate_address,
            self.validate_height,
            self.validate_weight,
            self.validate_hb,
            self.validate_head_circumference,
            self.validate_vision_data
        ]

        valid_df = df
        invalid_rows = []

        for validator in validators:

            valid_df, invalid_df = validator(valid_df)

            if not invalid_df.empty:
                invalid_rows.append(invalid_df)

        if invalid_rows:
            final_invalid_df = pd.concat(invalid_rows, ignore_index=True)
        else:
            final_invalid_df = pd.DataFrame()

        return valid_df, final_invalid_df

