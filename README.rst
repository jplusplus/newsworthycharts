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

These settings are available for all chart types:

- data: A list of datasets
- annotate_trend = True  # Print out values at points on trendline?
- trendline = []  # List of x positions, or data points
- yline = None  # A horizontal line across the chart (Matplotlib: axhline)
- labels = []  # Optionally one label for each dataset
- annotations = []  # Manually added annotations
- interval = None  # yearly|quarterly|monthly|weekly|daily
- units = 'number'  # number|percent|degrees
- show_ticks = True  # toggle category names, dates, etc
- subtitle = None
- note = None
- xlabel = None
- ylabel = None
- caption = None
- highlight = A position (typically a date, category label or index) to highlight. The semantics may differ somewhat between chart types.
- highlight_annotation = True  # Print out values at highlighted point?
- decimals = None  # None means automatically chose the best number
- logo = None  # Path to image that will be embedded in the caption area. Can also be set though a style property
- color_fn = None  # Custom coloring function

**SerialChart**

- type = 'line'  # line|bar|stacked_bar
- bar_width = 0.9  # percent of data point width
- allow_broken_y_axis = True|False  # default depends on chart type
- baseline = 0  # The “zero” line. Useful for plotting deviations, e.g. temperatures above/below mean
- baseline_annotation = None  # A label for the baseline
- line_width = None  # To override style settings
- max_ticks = 7  # Maximum number of ticks on the x axis
- ticks = None  # Custom ticks on the x axis, as a list of lists or tuples: `[(2013-01-01, "-13"), (2014-01-01, "-14"), (2015-01-01, "-15")]`
- ymin = None  # Minimum value on y axis. If None, it will be calculated from data
- ymax = None  # Maximum value on y axis. If None, it will be calculated from data
- colors = None  # A list of colors, each correspoding to one dataseries. Default behaviour is to use the style colors
- value_labels = False  # Print out values at points on line?
- highlighted_x_ranges = []  # List of tuples with start and end of highlighted areas
- x_range_labels = []  # List of labels for highlighted areas
- label_placement = "legend"  # legend|inline|outside
- color_labels = None  # A dictionary of label/color, to override style colors

**SeasonalChart**

**BubbleMap**

- bubble_size = 1  # The size of the bubbles

**CategoricalChart**

- bar_orientation = "horizontal"  # [horizontal|vertical]
- annotation_rotation = 0
- stacked = False
- legend = True
- colors = None

**CategoricalChartWithReference**

**Map**

- bins = 9  # Number of bins for continuous data
- binning_method = "natural_breaks"
- colors = None
- color_ramp = "YlOrRd"
- categorical = False  # If True, the map will be colored by category. If False, it will be colored by a continuous value
- base_map = None
- missing_label = None  # Add a label for no data

`basemap` can be `{ISO}-{level}` or `{ISO}|{subset}-{level}`. 
For example, `se-4` will show Swedish counties, while `se|03-7` will show municipalities (`se-7`) starting with `03`.

**ChoroplethMap**

_ Inherits from Map _

**ProgressChart**

**RangePlot**

**ScatterPlot**

**StripeChart**

Developing
----------

To run tests:

.. code-block:: python3

  python3 -m flake8
  python3 -m pytest

Deployment
----------

To deploy a new version to [PyPi](https://pypi.org/project/newsworthycharts):

1. Update Changelog below.
2. Update the version number in newsworthycharts/__init__.py
3. Create and push a git tag: `git tag VERSION; git push --tags` (not strictly needed, but nice)
4. Build: `python3 setup.py sdist bdist_wheel`
5. Check: `python3 -m twine check dist/newsworthycharts-X.Y.X*`
6. Upload: `python3 -m twine upload dist/newsworthycharts-X.Y.X*`

...assuming you have Twine installed (`pip3 install twine`) and configured.

Roadmap
-------
  - Adding more base maps
  - Getting rid of custom settings-hack
  - Custom month locator with equal-width month bars

Changelog
---------

- 1.59.0

  - Added `.highlight_annotation` to enable turning off the textual annotation on the highlighted point

- 1.58.0

  - Matplotlib==3.9
  - Added `.x_range_labels` to SerialChart
  - Some tweaks to title placement to avoid cropping of diactritics

- 1.57.3

  - Make NW region keys work with map subsets (e.g. `SE|03-7`)
  - Don't crash on subsequent calls to basemap parser

- 1.57.2

  - reduce excessive padding in categorical vertical charts
  - improved padding and margin logic for titles/subtitles (taking line spacing into account)

- 1.57.1

  - Fix missing outline in choropleth maps
  - matplotlib==3.8.4; Pillow==10.3.0

- 1.57.0

  - Changed z-ordering so that line are always on top of bars, and ylines/zero lines are behind lines but in front of bars
  - Avoid using the same color for trendline and lines
  - `yline` was moved to the SerialChart class, where it makes sense.

- 1.56.0

  - Reverted trendline behaviour to 1.54
  - Added `yline` to add a horizontal line across the chart (Matplotlib: axhline).

- 1.55.0

  - Always use neutral color for trendline

- 1.54.6

  - Improved logic for trendline coloring
  - Somewhat thinner trendline

- 1.54.5

  - Improved tick placement in daily charts
  - Minor upgrades: matplotlib==3.8.3; Pillow==10.2.0; geopandas==0.14.3

- 1.54.4

  - Use Babel 2.14, and pin version
  - Require numpy>=1.21.0 (now required by Matplotlib)
  - Patch upgrades: matplotlib==3.8.2; geopandas==0.14.1

- 1.54.3

  - Fix duplicated integer values in y axis

- 1.54.2

  - Make sure that legend is always on top of bars in stacked bar charts
  - Support more stacked categories in serial bar charts

- 1.52.2+

  - Backport various 1.54.x fixes

- 1.54.1

  - Patch upgrade Matplotlib to 3.8.1

- 1.54.0

  - Treat 'jpeg' format as 'jpg'
  - Fixed a rendering bug in stacked bar charts with multiple values being 0
  - Pillow upgraded to 10.1

- 1.53.0

  - Fixed bug in value_labels, trying to access a color value that didn't exist
  - Dropped Python 3.8 support (upstream)
  - Uses Matplotlib 3.8
  - Uses Pillow 10

- 1.52.1

  - Fixed date formatting issue in daily charts

- 1.52.0

  - No longer render EPS files by default.

- 1.51.2

  - _Really_ fix dependencies

- 1.51.1

  - Fix error in dependency verison

- 1.51.0

  - Added `BubbleMap`
  - Added `se-4` basemap for Swedish counties
  - Basemaps can now have multiplygons
  - Downgraded adjustText to 0.7.3, as upgrade broke rendering constistency in some places

- 1.50.2

  - Revert `matplotlib-label-lines` to previous version. 

- 1.50.0

  - Dropped Python 3.7 support (upstream)
  - Pinned Pillow to exact version in setup.py, for consistent rendering
  - `StripeChart`: First draft

- 1.49.1

  - `ProgressChart`: Better value label placement. 

- 1.49.0

  - `ProgressChart`: Enable custom value labels as third argument in data serie.

- 1.48.2
  
  - Bug fix: Handle translation in inset maps in `ChoroplethMap`. 

- 1.48.1

  - Bug fix: Path to translation file in `ChoroplethMap`. 

- 1.48.0

  - `ChoroplethMap`: Allow Newsworthy region names.
  - `RangePlot`: Re-add `start_label` that had been (mistakenly?) commented out.

- 1.47.2

  - Bug fix: Fixes legend issue in `ProgressChart`. 

- 1.47.1

  - Data point annotation now works for serial charts as well
  - Bug fix: Re-enable `qualitative_colors` as `color` argument in SerialChart (line). 

- 1.47.0

  - Support for rendering jpeg files, as `jpg`
  - Minimum required Python version is now 3.7 (jumping from 3.5)
  - Matplotlib@3.7.1

- 1.46.3

  - Fix z-ordering issue on multiple series (n > 2)

- 1.46.2

  - Fix tag mismatch in dist

- 1.46.1

  - Add missing haversine transform for non-projected crs

- 1.46.0
  
  - `height` can be set to None for automatic ratio, for chart types that support it. Will default to 1:1 for most chart types, but maps will try to provide a reasonable default based on geometry. Some chart types still require explicit height
  - It is now possible to use subsets of basemaps, by specifying a prefix: `se|03-7` means regions starting with `03` in `se-7`
  - Added .missing_label to ChoroplethMap. If None (default), no label will be printed.
  - Always accentuate base_line (/y=0), and make sure that line is on top of any bars to avoid “floating” bars
  - Improved error handling in ChoroplethMap
  - Clean up figure layout logic (this should speed up rendering somewhat)

- 1.45.0

  - Increased default `max_ticks` in SerialChart to 7
  - Matplotlib==3.7.0
  - adjustText==0.8.0
  - ChoroplethMap legend formatting, following language, decimals and units settings, etc
  - Minor tweaks to the layout algorithm. Might affect padding in some charts.
  - ChoroplethMap now does some basic normalizing of region codes
  - Added some data sanity checks, and improved error messages in ChoroplethMap
  - Added tests for ChoroplethMap

- 1.44.4
  
  - Do not default to broken y axis if chart contains a bar series.

- 1.44.3
  
  - Fix bug and occasional crash when using baseline with None values

- 1.44.2
  
  - Fix crash in serialchart coloring chain

- 1.44.1
  
  - Fix regression in SeasonalChart bar coloring

- 1.44.0
  
  - Added grey outline to choropleth maps
  - The `type` argument is now a list with one type per data serie. Using a string is still supported for backwards compability. This makes it possible to make mixed type charts.
  - Reworked, simpler and more stable bar coloring algorithm
  - The `type` argument is no longer a getter/setter
  - Reduced edge for bar chartswith many bars
  - Removed unused, undocumented special colors value `"qualitative_colors"`. We have reasonable defaults for all chart types, that can already be overridden. The qualitative colors are used by default for qualitative data.
  - Removed unused, undocumented support for highlighting a series by label, rather than a value. The first series is highlighted by default, and that behaviour can already be overriden by the `.colors` setting

- 1.43.4

  - Add more space for label title on se-7 maps

- 1.43.3

  - Don't try to render map insets with no data
  - Use style colors in categorical choropleth maps
  - Added missing support for coloring categorical maps with `.colors`
  - Make automatic labeling work on categorical maps with `.colors`
  - Somewhat lighter fill for missing values in choropleth maps (lightgray -> gainsboro)
  - Testing experimental label_title support, to be documented in 1.44.0

- 1.43.2

  - Fixed weird ymax in some baseline cases
  - Added bottom padding when baseline was below data-min  

- 1.43.1

  - Fixed cut off-bug with negative baseline
  - Fix coloring bug in warm_cold color_fn with baseline 
  - Fix regression with quarterly locator

- 1.43.0

  - Default to weekdays on x-axis if data spans 7 days or less
  - Added `.color_labels` to label bar colors set by `.color_fn`

- 1.42.0

  - Added `.baseline` setting for bar charts
  - `warm_cold` coloring algorithm now works relative `.baseline`
  - Added `.baseline_annotation`
  - `.color_fn` can now be a lambda function (or the name of one of the built in functions), e.g. `chart.color_fn = lambda x: "red" if x < 1.4 else "green"`
  - Bar charts will now always have a small white edge
  - Don't break y axis if data is close to 0
  - Offset quarters will be recognosed as quarters now (e.g. Feb, May, Aug, Nov)
  - Fixed bug in .allow_broken_y_axis implementation, causing y-axis to be broken in too many places
  - Various dependency updates
  - Replaced deprecated PIL.Image.ANTIALIAS with PIL.Image.Resampling.LANCZOS for logotype resizing.
  - Get rid of warnings about missing “glyph 10” when prerendering text to calculate text bos sizes
  - Fixed bug where single values surrounded my None's were not printed out in serial-data line charts. This was an earlier regression that was not noticed for many releases.

- 1.41.0

  - New, experimental chart type: Choropleth maps! Supports both categorical and continuous data. 
  - Better support for monthly time series spanning years
  - Fixed bug where missing annotation slots could crash CategoricalChart

- 1.40.2

  - Don't crash on deprecation warning
  - Matplotlib upgraded from 3.6.2 to 3.6.3
  - Pin some critical requirement versions

- 1.40.1

  - Fix floating point bug in percent labels
  - Test fixes

- 1.40.0

  - Auto-decide `.decimals` if None
  - Round 0.5 to 1, etc in value axis labels and annotations (the `ROUND_HALF_UP` behaviour)
  - Add `.force_decimals` to print out e.g. ”1.0”. Requires `.decimals` to be explicitly set
  - Serial Chart: Allow disabling ”broken y axis” feature by setting `allow_broken_y_axis=False`
  - Deprecated `units="count"`. Make all numbers equal. Use `units="number"` and `decimals=0` to get the earlier behaviour.
  - Remove overriding of decimal settings by units = count
  - Remove noisy deprecation warning on user settings in rc files
  - Formatters will now use the correct minus signs for the given locale.

- 1.39.1

  - Added missing metadata to svg
  - Added .__version__ attribute to the package

- 1.39.0

  - Added pdf export, now more widely used than eps
  - Author and software metadata now added to pdf and png, including the exakt NWCharts version used to produce an image

- 1.38.2
  
  - `S3Storage`: Handle text files.

- 1.38.1

  - Prevent logo from ever being > 155px, to restore previous behaviour.

- 1.38.0

  - Made multi series bar seasonal bar charts work for opposite signs, so that we can make +/- charts

- 1.37.3

  - Bug fix: Don't crash with factor argument in DW charts.

- 1.37.2

  - Fixed rendering bug in non-transparent eps exports with transparent logos

- 1.37.1

  - Fixed bug in argument parsing in S3Storage.save()

- 1.37.0

  - Added `storage_options` argument to `render()` and `render_all()`
  - Unified function signatures across storage classes.

- 1.36.0

  - Added options argument to `S3Storage.save()`

- 1.35.0

  - Enable logo scaling. Provided logos can now be any size, and will be scaled down to an appopriate format.

- 1.34.0

  - Adds `factor` argument to `.render()` and `.render_all()`.
  - Adds missing `transparent` argument to `.render_all()`.
  - Matplotlib @ 3.6.2
  - langcodes @ 3.3 to ensure consistent handling of macro languages (`no` is a valid language)

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
