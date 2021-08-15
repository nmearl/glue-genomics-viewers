def demo():

    from glue.core import DataCollection, Data
    from glue.app.qt import GlueApplication

    from .qt import setup

    setup()

    dc = DataCollection([Data(x=[1,2,3], label='data')])
    ga = GlueApplication(dc)
    ga.start()


if __name__ == "__main__":
    demo()