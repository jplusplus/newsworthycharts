This  module contains methods for producing graphs and publishing them on Amazon S3, or in the location of your choice.

It is written and maintained for `Newsworthy <https://www.newsworthy.se/en/>`_, but could possibly come in handy for other people as well.

By `Journalism++ Stockholm <http://jplusplus.org/sv>`_.

Installing
----------

.. code-block:: bash

  pip install newsworthy-charts


Using
-----

This module comes with two classes, `Chart` and `Storage` (and it's subclasses).
When using the Chart class, the generated chart will be saved as a local file:

.. code-block:: python3

  from newsworthycharts import SerialChart


  c = Chart(600, 800)
  c.title = "Number of smiles per second"
  c.xlabel = "Time"
  c.ylabel = "Smiles"
  c.caption = "Source: Ministry of smiles."
  data_serie_1 = [("2008-01-01", 6.1), ("2009-01-01", 5.9), ("2010-01-01", 6.8)]
  c.data.append(data_serie_1)
  c.highlight = "2010-01-01"
  c.render("test", "png")

You can use a _storage_ object to save file to
a specific location or cloud service:

.. code-block:: python3

  from newsworthycharts import Chart
  from newsworthycharts import S3Storage

  s3 = S3Storage("my_bucket")
  c = Chart(600, 800, storage=s3)
  c.title = "Number of smiles per second"
  c.xlabel = "Time"
  c.ylabel = "Smiles"
  c.caption = "Source: Ministry of smiles."
  c.render("test", "png")


To store a file in a local folder, use the `LocalStorage` class:

.. code-block:: python3

  from newsworthycharts import LocalStorage

  storage = LocalStorage("/path/to/generated/charts")

Charts are styled using built-in or user-defined styles:

.. code-block:: python3

  from newsworthycharts import Chart

  # This chart has the newsworthy default style
  c = Chart(600, 800, style="newsworthy")

  # Style can also be the path to a style file (absolute or relative to current working directory)
  c2 = Chart(600, 800, style="path/to/styles/mystyle.mplstyle")

To set up you own style, copy the build-in default: <https://github.com/jplusplus/newsworthycharts/blob/master/newsworthycharts/rc/newsworthy>

Newsworthycharts will look first among the predefined style files for the requested style, so if you have a custom style file in you working directory you need to give it a unique name not already in use.

Changelog
---------

- 1.0.0.dev*
  - First version, still in development
