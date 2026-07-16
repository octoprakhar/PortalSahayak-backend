from all_models.ChildRunResult import ChildRunResult

def to_report_row(result: ChildRunResult) -> dict:

        child = result.child

        return {
            "Name": child.name,
            "DOB": child.dob,
            "Father Name": child.fatherName,
            "Mother Name": child.motherName,
            "Mobile": child.mobileNumber,
            "Gender": child.gender,
            "Address": child.address,

            "Child Type": result.child_type.value,

            "Original Height": child.height,
            "Final Height": result.final_height,

            "Original Weight": child.weight,
            "Final Weight": result.final_weight,

            "Original HB": child.hb,
            "Final HB": result.final_hb,

            "Original Head Circumference": child.headCircumference,
            "Final Head Circumference": result.final_head_circumference,

            "Original Disease": child.diseaseName,
            "Final Disease": ", ".join(result.final_diseases),

            "Stage": result.stage.name,

            "Status": result.feedback.outcome.value if result.feedback else "",

            "Message": result.feedback.message if result.feedback else "",

            "Validation Errors": (
                "; ".join(result.feedback.validation_errors)
                if result.feedback
                else ""
            ),
        }