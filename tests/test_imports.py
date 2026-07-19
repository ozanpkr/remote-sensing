def test_imports():
    from remote_sensing import Analyzer, RasterHandler, AreaType
    assert Analyzer is not None
    assert RasterHandler is not None
    assert AreaType.BURNED.name == 'BURNED'
