import enum

class ResultType(enum.Enum):
    terreno = "terreno"
    propriedade = "propriedade"

class ResultStatus(enum.Enum):
    visualized = "visualized"
    processing = "processing"
    finished = "finished"
    failed = "failed"
