==================
pyEvaluationEngine
==================

This is the documentation of **pyEvaluationEngine**. The package builds upon the OpenML project.

Contents
========

.. toctree::
   :maxdepth: 2

   Overview <readme>
   Contributions & Help <contributing>
   License <license>
   Authors <authors>
   Changelog <changelog>
   Module Reference <api/modules>


How to install pyEvaluationEngine
=================================
You can install the package an CLI interface by using the provided setuptools.

.. code:: bash

    python setup.py install

The entrypoint for scripts is the ``cli.py`` file. After installation, the scripts can be ran with ``pyevaluationengine``. For more specific information about parameters, add the ``-h`` flag.


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

