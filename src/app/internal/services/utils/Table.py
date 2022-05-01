from prettytable import FRAME, PrettyTable


class Table(PrettyTable):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.vrules = FRAME
        self.padding_width = 3
