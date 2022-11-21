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

You can use one of the predefine chart classes to make common chart types. Or you can use Newsworthycharts together with Matplotlib. This is useful is you just want to add text elements such as subtitle, notes or apply a predefine theme.

Here is how you would make a pie chart:

.. code-block:: python3

  # data
  labels = 'Frogs', 'Hogs', 'Dogs', 'Logs'
  sizes = [15, 30, 45, 10]

  # setup chart
  chart = Chart(width=800, height=600, storage=local_storage)
  chart.title = "My pie chart"
  chart.subtitle = "Look at all those colors"

  # NB: Render the chart to `chart.ax`
  chart.ax.pie(sizes, labels=labels, autopct='%1.1f%%')

  # Save the chart
  chart.render("tailored_chart", "png")

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

Options
-------

**Chart**
data: A list of datasets
annotate_trend = True  # Print out values at points on trendline?
trendline = []  # List of x positions, or data points
labels = []  # Optionally one label for each dataset
annotations = []  # Manually added annotations
interval = None  # yearly|quarterly|monthly|weekly|daily
show_ticks = True  # toggle category names, dates, etc
subtitle = None
note = None
xlabel = None
ylabel = None
caption = None
highlight = None
decimals = None
# number of decimals to show in annotations, value ticks, etc
# None means automatically chose the best number
logo = None
# Path to image that will be embedded in the caption area
# Can also be set though a style property
color_fn = None
# Custom coloring function

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
3. Create a git tag: `git tag VERSION` (not strictly needed, but nice)
4. Build: `python3 setup.py sdist bdist_wheel`
5. Upload: `python3 -m twine upload dist/newsworthycharts-X.Y.X*`

...assuming you have Twine installed (`pip install twine`) and configured.

Changelog
---------

- next

  - Matplotlib @ 3.6.2

- 1.33.0:
  
  - Adds `transparent` argument to render method.

- 1.32.3

  - `ScatterPlot`: Mark labeled dots more clearly.

- 1.32.2

  - `SerialChart`: Better error when timepoints are duplicated.

- 1.32.1

  - Bug fixes: Handle negative values when `ymin=0` in SerialChart and remove line stroke from `highlighted_x_ranges`.

- 1.32.0

  - `SerialChart`: New options: `line_width` and `highlighted_x_ranges`. 

- 1.31.0

  - Added `label_placement='outside'` option to SerialChart

- 1.30.0

  - Matplotlib updated from 3.3 to 3.6, including among many, many other things:
    - support for .webp
    - a lot of additions and improvements to rcParams
    - new backends
  - Custom NWCharts parameters to the rc style file is being deprecated, and should eventually be phased out
  - Matplotlib and related modules are now pinned to a specific version
  - Added support for generating webp images!
  - Upgraded pytest to support Python 3.10+
  - Fixed date locators to use thecorrect langauge/locale
  - Added padding on top of title, to avoid cropping diactritics

- 1.29.0

  - `CategoricalChart`: Make it possible to hide legend. 

- 1.28.1

  - `CategoricalChartWithReference`: Handle multi color bars. 

- 1.28.0

  - `Chart` / `SerialChart`: New feature: Mark broken y axis with symbol.

- 1.27.1

  - `SerialChart`: Force y axis range to to given values when `ymax` and `ymin` is defined.

- 1.27.0

  - `SerialChart`: Enable value labeling of each point on line.

- 1.26.1

  - Highlight only current value in SeasonalChart; use different shades of grey for the rest

- 1.26.0

  - Add `SeasonalChart`, a.k.a the Olsson chart

- 1.25.3

  - ProgressChart: Handle missing values
  - `lib.formatter.Formatter`: Handle null values

- 1.25.2

  - ScatterPlot: Enable ymin and xmin in scatterplot.

- 1.25.1

  - Color annoation outline by background color.

- 1.25.0

  - Improved ScatterPlot.

- 1.24.1

  - Bug fix: Inline labeling on charts with missing data.

- 1.24.0

  - CategoricalChartWithReference: Adds highlight option

- 1.23.1

  - Adds missing dependency.

- 1.23.0

  - SerialChart: Introduces inline labeling on lines

- 1.22.1

  - Tweeks on line labeling

- 1.22.0

  - SerialChart: Introduces labeling on lines (rather than just legends)

- 1.21.5

  - Bug fix: Handle charts without ticks to be able to render pie charts again

- 1.21.4

  - Beter height handling in header and footer.
  - Make Noto Sans default font.

- 1.21.3

  - Enable colors property in stacked bar SerialChart.

- 1.21.2

  - Adjusts x margin in RangePlot to fit value labels better.
  - Increases line spacing in subtitle.

- 1.21.1

  - Bug fix: Small change in Datawrapper API.
  - Make ticks option work with SerialChart.init_from

- 1.21.0

  - New feature: Use base `Chart` class to make custom charts.
  - Bug fix: Labels outside canvas in RangePlot

- 1.20.2

  - ClimateCars: Tweeks on 2030 chart.

- 1.20.1

  - Handle np.int as years.

- 1.20.0

  - CategoricalChart: Highlight multiple values with list
  - Bug fix: ylabel placed outside canvas
  - Style: Align caption with note

- 1.19.2

  - RangePlot: Better label margins and bold labels.

- 1.19.1

  - RangePlot: Rename argument values_labels => value_labels.


- 1.19.0

  - Pick up qualitative colors from style file.

- 1.18.1

  - Fixed coloring on highlighted progress charts.
  - Adds ability to highlight both ends on range plot.

- 1.18.0

  - Added `ticks` option to SerialChart, to set custom x-axis ticks
  - Added color option to CategoricalChart, to work exactly as in SerialChart
  - Fixed bug with highlight in line charts where some line was outside the highlighted date.


- 1.17.0

  - Enable multiple targets in progress chart.

- 1.16.2

  - Fixes highlight bug in progress chart.

- 1.16.1

  - Small changes in range plot.

- 1.16.0

  - Adds CO2 budget chart

- 1.15.2

  - ClimateCar chart tweeks.

- 1.15.1

  - Bug fix: Adds newsworthycharts.custom to build.

- 1.15.0

  - Introduces progress charts and removes hard coded font sizes.

- 1.14.0

  - Introduces range plots and enables custom coloring in serial charts.

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
