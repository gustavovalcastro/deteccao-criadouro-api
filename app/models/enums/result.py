import enum

class ResultType(enum.Enum):
    terreno = "terreno"
    propriedade = "propriedade"

class ResultStatus(enum.Enum):
    visualized = "visualized"
    finished = "finished"
    processing = "processing"
    failed = "failed"
