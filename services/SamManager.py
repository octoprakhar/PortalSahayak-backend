class SamManager:
    """
    It will just help to check whether we can add this child to SAM or not.
    One instance must be used per workflow.
    """

    def __init__(self, max_sam: int = 1):
        self.max_sam = max_sam
        self.curr_sam = 0

    def can_accept_sam(self):
        return self.curr_sam < self.max_sam
    
    def register_sam(self):
        self.curr_sam += 1