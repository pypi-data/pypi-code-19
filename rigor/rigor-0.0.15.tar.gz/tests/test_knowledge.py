from rigor import Suite


def test_execute():
    directories = ["/Users/ianmaurer/code/knowledge/qa/consult"]
    suite = Suite(directories=directories, tags_excluded=["broken"])
    result = suite.execute()
    # assert result.success
    # assert len(result.passed) == 1
