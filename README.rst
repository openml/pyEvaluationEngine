===============================
OpenML Python Evaluation Engine
===============================

.. image:: https://github.com/openml/pyEvaluationEngine/actions/workflows/tox.yml/badge.svg
    :target: https://github.com/openml/pyEvaluationEngine/actions/workflows/tox.yml


Python port of the OpenML `Evaluation Engine`_

Installation
=================================
Preferably you want to setup a virtual environment first to prevent the package from being installed to your global python installation. You can install the package with the CLI interface by using the provided setuptools.

.. code:: bash

    python setup.py install

After installation, the scripts can be ran with the following command: ``pyevaluationengine``. For more specific information about parameters, add the `-h` flag. The entrypoint for scripts is configured to be the ``cli.py`` file.

To see more specific instructions on how to install this package as a development dependency, we recommend looking the the CONTRIBURING file and follow some of the steps under the "Code Contributions" header.

Usage
=====
The CLI has the following modes:

config
    Used to set the API key and URL. This command needs to be run before you can use any of the other scripts.

all
    Processes and analyzes all of the unprocessed datasets once.

print
    Prints all of the unprocessed datasets to the terminal.

singular
    Processes the specified dataset by name.

amount
    Processes a specified amount of datasets

repeat
    Processes all unprocessed datasets and repeats this after a specified timeout


Further information
===================

* `OpenML documentation <https://docs.openml.org/>`_
* `OpenML client APIs <https://docs.openml.org/APIs/>`_
* `OpenML developer guide <https://docs.openml.org/Contributing/>`_
* `Contact information <https://www.openml.org/contact>`_
* `Citation request <https://www.openml.org/cite>`_
* `OpenML blog <https://medium.com/open-machine-learning>`_
* `OpenML twitter account <https://twitter.com/open_ml>`_


.. _Evaluation Engine: https://github.com/ludev-nl/2021-01-pyEvaluationEngine
