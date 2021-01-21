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
  c.subtitle = "This chart tells you something very important."
  c.xlabel = "Time"
  c.ylabel = "Smiles"
  c.note = "There are some missing smiles in data"
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

  python3 -m flake8
  python3 -m pytest

Deployment
----------

To deploy a new version to PyPi:

1. Update Changelog below.
2. Update `version.py`
3. Build: `python3 setup.py sdist bdist_wheel`
4. Upload: `python3 -m twine upload dist/newsworthycharts-X.Y.X*`

...assuming you have Twine installed (`pip install twine`) and configured.

Changelog
---------

- 1.13.3

  - Fit long ticks on y axis.

- 1.13.2

  - Set annotation fontsize to same as ticks by default. 

- 1.13.1

  - Bug fix: Subtitle placement

- 1.13.0

  - Introduces subtitle and note.
  - Updates default styles to align with Newsworthy style guide.


- 1.12.1

  - Fit footer by logo height. Fixes bug that caused axis overlag when logo was large.

- 1.12.0

  - Introduces stacked categorical bar charts

- 1.11.2

  - Bug fix: Remove failing attemt to store chart in dw format


- 1.11.1

  - Corrects zorder and centers tick on CategoricalChartWithReference

- 1.11.0

  - Introduces new chart: CategoricalChartWithReference

- 1.10.1

  - Fixes bad X ticks in weekly SerialChart (and charts that don't start in January).

- 1.10.0

  - Add annotation_rotation option to categorical charts
  - Fix a crash in some special cases with serial charts shorter than a year.
  - Fix a bug where diff between series was not highlighted if one value was close to zero.

- 1.9.2

  - Include translations in build.

- 1.9.1

    - Translates region to Datawrapper standard when making maps.

- 1.9.0

    - Allows list of dicts to be passed to DatawrapperChart to be make tables, categorical maps etc.

- 1.8.2

    - Require requests.

- 1.8.1

  - Bug fixes.

- 1.8.0

  - Introduces Datawrapper Chart type.

- 1.7.0

  - Adds ymax argument (to SerialChart)
  - Bug fix: Handle missing values in SerialChart with line.

- 1.6.12

  - Bug fix: Set y max to stacked max in stacked bar chart.

- 1.6.11

  - Introduces stacked bars to SerialChart.

- 1.6.10

  - Fixes bar_orientation bug with `init_from()`

- 1.6.9

  - Fix an ugly bug where type=line would not work with `init_from()`

- 1.6.8

  - Some cosmetic changes: no legend if only one series, color updates, thinner zero line.


- 1.6.7

  - Make title and units work with `init_from` again

- 1.6.6

  - Add warm/cold color function

- 1.6.5

  - Really, really make `init_from` work, by allowingly allowing allowed attributes

- 1.6.4

  - Fix bug where `init_from` would sometime duplicate data.
  - Make sure `init_from` does not overwrite class methods.

- 1.6.3

  - Protect private properties from being overwritten by `init_from`
  - When `units` is count, `decimal` should default to 0 if not provided. This sometimes didn't work. Now it does.

- 1.6.2

  - Make `init_from` work as expected with a language argument

- 1.6.1

  - Make `init_from` work as expected with multiple data series

- 1.6.0

  - Added a factory method to create charts from a JSON-like Python object, like so: `SerialChart.init_from(config, storage)`

- 1.5.1

  - Fix packaging error in 1.5.0

- 1.5.0

  - Expose available chart engines in `CHART_ENGINES` constant for dynamic loading
  - Add `color_fn` property, for coloring bars based on value
  - Increase line width in default style
  - Upgrading Numpy could potentially affect how infinity is treated in serial charts.

- 1.4.1

  - Revert text adjusting for categorical charts, as it had issues

- 1.4.0

  - Add new ScatterPlot chart class
  - Improved text adjusting in serial charts
  - More secure YAML file parsing

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
