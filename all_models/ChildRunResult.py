from dataclasses import dataclass,field

from all_models.child_models import Child
from all_models.FeedbackResult import FeedbackResult,FeedbackOutcome
from constants.WorkflowStage import WorkflowStage
from constants.ChildType import ChildType


@dataclass
class ChildRunResult:
    
    """
    Personal detail entering and final data entering both will return it. At the moment when failure is shown just add it to respective ReportCreator
    """

    child: Child
    child_type: ChildType = ChildType.EXISTING_CHILD

    final_height: str | None = None
    final_weight: str | None = None
    final_hb: str | None = None
    final_head_circumference: str | None = None

    final_diseases: list[str] = field(default_factory=list)

    feedback: FeedbackResult | None = field(
        default_factory=lambda:
            FeedbackResult(
                outcome=FeedbackOutcome.SYSTEM_ERROR,
                message="Feedback not assigned"
            )
    )
    stage:WorkflowStage = WorkflowStage.HEALTH_DETAILS
    