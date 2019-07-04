This  module contains methods for producing graphs and publishing them on Amazon S3, or in the location of your choice.

It is written and maintained for `Newsworthy <https://www.newsworthy.se/en/>`_, but could possibly come in handy for other people as well.

By `Journalism++ Stockholm <http://jplusplus.org/sv>`_.

Installing
----------

.. code-block:: bash

  pip install newsworthycharts


Using
-----

This module comes with two classes, `Chart` and `Storage` (and it's subclasses).
When using the Chart class, the generated chart will be saved as a local file:

.. code-block:: python3

  from newsworthycharts import SerialChart as Chart


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

Developing
----------

To run tests:

.. code-block:: python3

  python3 -m pytest test/test_main.py

Changelog
---------

- 1.3.3

  - Make small bar charts with very many bars look better

- 1.3.2

  - Make labels work again, 1.3.1 broke those in some circumstances
  
- 1.3.1

  - Make inner_max/min_x work with leading / trailing None values
  - Make sure single, orphaned values are visible (as points) in line charts

- 1.3.0

  - Allow (and recommend) using Matplotlib 3. This may affect how some charts are rendered.
  - Removed undocumented and incomplete Latex support from caption.
  - Don't highlight diff outside either series' extreme ends.
  
- 1.2.1

  - Use strong color if there is nothing to highlight.

- 1.2.0

  - Fix a bug where `decimals` setting was not used in all annotations. Potentially breaking in some implementations.
  - Make the annotation offset 80% of the fontsize (used to be a hardcoded number of pixels)

- 1.1.5

  - Small cosmetic update: Decrease offset of annotation.

- 1.1.4

  - Require Matplotlib < 3, because we are still relying on some features that are deprecated there. Also, internal changes to Matplot lib may cause some charts to look different depending on version.

- 1.1.3

  - Make annotation use default font size, as relative sizing didn't work here anyway

- 1.1.2

  - Move class properties to method properties to make sure multiple Chart instances work as intended/documented. This will make tests run again.
  - None values in bar charts are not annotated (trying to annotate None values used to result in a crash)
  - More tests

- 1.1.1

  - Annotations should now work as expected on series with missing data

- 1.1.0

  - Fix bug where decimal setting wasn't always respected
  - Make no decimals the default if unit is "count"

- 1.0.0

  - First version
