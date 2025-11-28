def test_import_ingestor():
    import importlib
    importlib.import_module("src.ingestor.ingestor")  # or correct path


def test_import_processor():
    import importlib
    importlib.import_module("src.processor.processor")


def test_import_trainer():
    import importlib
    importlib.import_module("src.trainer.train_baseline")


def test_import_server():
    import importlib
    importlib.import_module("serving.server")
